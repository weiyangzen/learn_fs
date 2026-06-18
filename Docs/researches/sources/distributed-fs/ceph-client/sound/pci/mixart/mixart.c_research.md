# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.c

## Purpose
This is the main ALSA/PCI entry point for Digigram miXart cards. It creates the shared board manager, maps PCI BARs, requests the threaded IRQ, allocates up to four ALSA card instances for one physical board, allocates firmware-visible flow and buffer descriptor arrays, invokes firmware setup, and implements PCM pipe, stream, clock, open/close, hw_params, prepare, trigger, pointer, proc, probe, and remove behavior.

## Important APIs, types, and functions
The file uses `struct mixart_mgr`, `struct snd_mixart`, `struct mixart_pipe`, `struct mixart_stream`, `struct mixart_flowinfo`, and `struct mixart_bufferinfo` from `mixart.h`. `mixart_set_pipe_state` starts/stops firmware streaming groups through mailbox messages and synchronization commands. `mixart_set_clock` configures a pipe clock through `MSG_CLOCK_SET_PROPERTIES`. `snd_mixart_add_ref_pipe` lazily creates firmware stream groups and populates flow/buffer descriptors; `snd_mixart_kill_ref_pipe` releases references and deletes firmware groups.

PCM callbacks include `snd_mixart_playback_open`, `snd_mixart_capture_open`, `snd_mixart_close`, `snd_mixart_prepare`, `snd_mixart_hw_params`, `snd_mixart_hw_free`, `snd_mixart_trigger`, and `snd_mixart_stream_pointer`. `mixart_set_format` converts ALSA PCM formats into firmware `mixart_stream_param_desc` values. `snd_mixart_pcm_analog`, `snd_mixart_pcm_digital`, and `snd_mixart_create_pcm` create ALSA PCM devices. `snd_mixart_probe` and `snd_mixart_remove` implement PCI lifecycle.

## Control flow
Probe enables the Motorola PCI device, sets bus mastering and a 32-bit DMA mask, allocates `mixart_mgr`, requests and maps BAR0/BAR1, installs a shared threaded IRQ, initializes mutexes/waitqueue/message counters, creates four ALSA cards, registers each low-level chip object, and initializes proc files on chip 0. It then allocates contiguous DMA pages for the flowinfo and bufferinfo arrays, zeros them, and calls `snd_mixart_setup_firmware`. Firmware setup completes hardware initialization, creates PCMs/mixer, and registers the cards after the embedded firmware is ready.

On playback or capture open, the driver chooses analog or digital capabilities from the PCM object, reserves the stream object, obtains a matching pipe through `snd_mixart_add_ref_pipe`, starts the pipe if needed, stores stream metadata in runtime private data, applies period/buffer step constraints, and pins later opens to the already-selected sample rate. `hw_params` updates mixer stream levels, sends stream format to firmware, and writes DMA buffer address/length into the shared bufferinfo entry. `prepare` drains nonblocking mailbox completions, records the first stream sample rate, and sets the pipe clock when the first reference prepares. `trigger` sends nonblocking start/stop stage packets and updates stream status. Timer notifications processed in `mixart_core.c` update `buf_periods` and `buf_period_frag`, which `pointer` returns.

Close decrements sample-rate reference count, deletes or dereferences the pipe, and marks the stream free. Free tears down all cards, mailbox interrupts, IRQ, board firmware state, BAR mappings, DMA descriptor arrays, PCI regions, and the manager.

## State and persistence behavior
Runtime state is split between the host manager/chip structures and firmware-visible DMA descriptor arrays. `mgr->sample_rate` and `mgr->ref_count_rate` enforce one active rate across open streams. Pipe state transitions through `PIPE_UNDEFINED`, `PIPE_STOPPED`, `PIPE_RUNNING`, and `PIPE_CLOCK_SET`; stream state transitions through free/open/running/pause. `flowinfo` and `bufferinfo` are persistent DMA allocations for the life of the manager and are passed to firmware after ELF load. No on-disk persistence exists.

## Dependencies and integration points
This file integrates ALSA card, PCM, proc, control, and DMA APIs with PCI probing and the miXart mailbox exported by `mixart_core.c`. Firmware and hardware discovery are delegated to `mixart_hwdep.c`; mixer controls and stream level updates are delegated to `mixart_mixer.c`. BAR helpers and firmware register constants come from `mixart_hwdep.h`; message IDs and payload structures come from `mixart_core.h`.

## Risks and edge cases
The driver assumes four logical cards per physical board and fixed descriptor indexing across card, PCM type, playback/capture, and substream number. A bad index calculation can corrupt firmware-visible descriptors. Nonblocking trigger messages depend on later IRQ processing; failure to drain `msg_processed` can race with prepare or hw_free. Sample-rate locking is global to the manager, which may reject otherwise valid mixed-rate use. Digital PCM creation depends on detected AES daughterboard type. Some cleanup paths call `snd_mixart_free` after partial initialization; all fields must remain safe for partial teardown.

## Test signals
Valuable tests include probe/remove with firmware present, card count and names for four logical cards, analog PCM playback/capture open-close loops, AES PCM creation only when the daughterboard is detected, stream start/stop notifications, pointer advancement from timer notifications, multi-stream same-rate enforcement, different-rate rejection after first open, proc reads for BAR data and board info, and fault injection for IRQ request, BAR mapping, DMA allocation, firmware setup, and card registration failures.

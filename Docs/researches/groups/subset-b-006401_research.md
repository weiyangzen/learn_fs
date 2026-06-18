# subset-b-006401 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/maestro3.c -->
# sources/distributed-fs/ceph-client/sound/pci/maestro3.c

## Purpose
This file is the complete ALSA PCI driver for ESS Maestro3, Allegro, and Canyon3D-2 audio controllers. It binds PCI IDs for the supported ESS devices, downloads ASSP firmware (`ess/maestro3_assp_kernel.fw` and `ess/maestro3_assp_minisrc.fw`), exposes one ALSA PCM device with two playback substreams and one capture substream, creates an AC97 mixer, handles hardware volume buttons, and implements suspend/resume by saving and restoring ASSP code/data memory.

## Important APIs, types, and functions
The core state is `struct snd_m3`, which owns the ALSA card, PCI device, I/O base, AC97 codec, PCM object, firmware handles, ASSP lists, stream array, interrupt lock, power-management save buffer, GPIO/quirk flags, and optional input-device or mixer-control references for hardware volume events. Per-stream state lives in `struct m3_dma`, including the ALSA substream pointer, ASSP code/data instance addresses, DMA buffer address/size, period accounting, and indices into ASSP mixer/minisrc/DMA lists.

The low-level register helpers `snd_m3_inb/outb/inw/outw`, `snd_m3_assp_read`, and `snd_m3_assp_write` are the hardware access boundary. `snd_m3_assp_init` loads the firmware words into internal ASSP code/data memory and seeds the kernel task list and mixer/DMA list descriptors. `snd_m3_assp_client_init` allocates per-substream minisrc data windows. `snd_m3_chip_init`, `snd_m3_enable_ints`, `snd_m3_ac97_reset`, and `snd_m3_mixer` perform device, interrupt, codec, and mixer setup.

The ALSA PCM callbacks are `snd_m3_substream_open`, `snd_m3_substream_close`, `snd_m3_pcm_hw_params`, `snd_m3_pcm_prepare`, `snd_m3_pcm_trigger`, and `snd_m3_pcm_pointer`. `snd_m3_pcm_setup1`, `snd_m3_playback_setup`, `snd_m3_capture_setup`, and `snd_m3_pcm_setup2` program the ASSP client instance for DMA pointers, sample format, channel mode, sample-rate conversion, and playback/capture direction.

`snd_m3_interrupt` services ASSP timer and hardware-volume interrupts. `snd_m3_update_ptr` translates ASSP DMA pointers into ALSA period notifications. `snd_m3_update_hw_volume` maps hardware volume-counter deltas into AC97 mixer updates or Linux input key events when `CONFIG_SND_MAESTRO3_INPUT` is enabled. Probe and module binding are handled by `__snd_m3_probe`, `snd_m3_probe`, `snd_m3_create`, and the `m3_driver` PCI driver object.

## Control flow
Probe filters out non-audio functions, allocates a managed ALSA card, selects a card name from the PCI device ID, and calls `snd_m3_create`. Device creation enables the PCI function, restricts DMA to 28 bits, applies subsystem quirks for amp GPIO, IrDA, hardware volume, and OmniBook GPIO handling, requests both firmware images, requests PCI regions, initializes the ASSP and AC97 codec, enables the external amp, requests the IRQ, allocates an optional suspend memory image, creates the AC97 mixer, initializes all per-stream ASSP clients, creates the PCM device, optionally registers an input device, enables interrupts, and starts the ASSP.

Opening a PCM substream reserves a free `m3_dma` slot under `reg_lock` and assigns it to playback mixer/minisrc/DMA lists or capture ADC/minisrc/DMA lists. `prepare` validates U8 or S16_LE format and 8-48 kHz rate, writes host DMA boundaries, DSP scratch buffer boundaries, playback/capture static parameters, and sample-rate conversion values. `trigger` flips the stream `running` flag and writes ASSP readiness bits; start increments timer users and either updates active DAC count or requests ADC capture, while stop reverses those changes. ASSP timer interrupts poll all running streams and call `snd_pcm_period_elapsed` when enough bytes have advanced.

Suspend sets `in_suspend`, cancels pending hardware-volume work, suspends AC97, halts the ASSP, and copies all code and data memory into `suspend_mem`. Resume reinitializes PCI/ASSP/AC97, rewrites the saved ASSP image, clears DMA active state, resumes AC97, restarts ASSP and interrupts, re-enables amp/GPIO handling, and restores ALSA power state.

## State and persistence behavior
Persistent runtime state is held in kernel memory and device registers only; no filesystem state is written by the driver. Firmware images are requested at probe and released in card private cleanup. ASSP code/data memory is mutable runtime state, including packed task/client lists, DMA pointers, mixer task count, timer reload values, and per-stream instance data. The stream list model is fragile: ASSP lists are packed arrays, so close removes a stream by copying the last list entry into the removed slot and zeroing the tail.

Power-management persistence is in `suspend_mem`, which snapshots ASSP memory across D3hot. Hardware-volume events are deferred to a work item so interrupt context only schedules processing. `in_suspend` suppresses interpreting spurious hardware-volume interrupts during suspend/resume.

## Dependencies and integration points
This driver integrates with the Linux PCI core, ALSA core, ALSA PCM, AC97 codec, firmware loader, optional input subsystem, IRQ handling, DMA mapping, and PM sleep callbacks. It depends on ESS-specific PCI config registers, legacy I/O BAR access, AC97 serial-bus protocol, GPIO-based amp and codec reset wiring, and two external firmware blobs. The source has disabled MIDI support behind `#if 0`, so MPU401 constants exist but are not exposed.

## Risks and edge cases
The hardware is programmed through many magic register and ASSP memory offsets; regressions are likely if offsets, firmware layout assumptions, or packed-list handling change. DMA is limited to 28 bits, so platforms without a suitable DMA mask fail probe. Firmware absence fails device creation. AC97 reset uses repeated timing-sensitive GPIO sequences and device-specific delays. Hardware-volume support relies on subsystem quirks and counter patterns; unknown systems can mis-handle buttons or amp GPIO polarity. The interrupt path drops `reg_lock` around `snd_pcm_period_elapsed`, so period accounting must remain consistent across concurrent stop/close paths. Resume depends on successful `suspend_mem` allocation; without it suspend/resume becomes a no-op for ASSP state.

## Test signals
Useful test signals include successful module probe with firmware present, ALSA card/PCM/mixer registration, playback and capture at U8 and S16_LE across 8-48 kHz, period interrupts advancing without underrun/overrun, AC97 mixer read/write behavior, hardware volume/mute button events on quirked laptops, amp GPIO audibility after probe/resume, suspend/resume while streams are idle and active, and negative tests for missing firmware or unsupported DMA masks. Kernel logs around `ac97 serial bus busy`, firmware request failure, ASSP memory allocation, IRQ request failure, and codec reset retries are high-value diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/maestro3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/Makefile

## Purpose
This Kbuild file defines the ALSA Digigram miXart PCI driver module. It composes the `snd-mixart` module from the driver entry point, mailbox/core logic, firmware loader, and mixer implementation.

## Important APIs, types, and functions
The relevant Kbuild variables are `snd-mixart-y`, which lists `mixart.o`, `mixart_core.o`, `mixart_hwdep.o`, and `mixart_mixer.o`, and `obj-$(CONFIG_SND_MIXART)`, which links `snd-mixart.o` when the kernel configuration enables `CONFIG_SND_MIXART`.

## Control flow
There is no runtime control flow. At build time, Kbuild compiles the four object files and links them into one ALSA PCI module. The module object then provides the `module_pci_driver` entry from `mixart.c`, while exported internal functions are resolved between the four objects.

## State and persistence behavior
The Makefile has no runtime state or persistence. Its only state is the static build graph encoded in Kbuild variables.

## Dependencies and integration points
It depends on the kernel Kbuild system and the `CONFIG_SND_MIXART` symbol. It is tightly aligned with the local source split: removing one listed object would break symbols such as `snd_mixart_send_msg`, `snd_mixart_setup_firmware`, or `snd_mixart_create_mixer`.

## Risks and edge cases
The primary risk is build skew: adding a new source file or moving functions between miXart files requires updating `snd-mixart-y`. If `CONFIG_SND_MIXART` is disabled, none of the miXart driver code is built, regardless of source presence.

## Test signals
Build tests should confirm that enabling `CONFIG_SND_MIXART=m` or `=y` produces `snd-mixart` without unresolved symbols and that disabling the config omits the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.h -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.h

## Purpose
This header defines the main miXart driver data model shared by the PCI/PCM, mailbox, firmware, and mixer files. It captures board-manager state, per-card state, firmware-visible buffer descriptors, stream/pipe status values, notification bit layout, and exported cross-file functions.

## Important APIs, types, and functions
`struct mixart_uid` is the firmware object identifier used by most mailbox requests. `struct mem_area` represents mapped PCI BARs. `struct mixart_mgr` is the physical-board manager: it owns the PCI device, IRQ, BAR mappings, mailbox wait/fifo state, locks, firmware status, board type, flow/buffer DMA allocations, console-manager UID, global sample rate, and mixer lock. `struct snd_mixart` is one logical ALSA card and stores PCM objects, analog/digital pipes, stream arrays, physical I/O UIDs, and cached mixer settings.

`struct mixart_pipe` models a firmware streaming group with connector UIDs, status, reference count, and monitoring flag. `struct mixart_stream` models one ALSA runtime stream and stores status, channel count, period-notification accounting, PCM number, and pipe reference. `struct mixart_bufferinfo` and `struct mixart_flowinfo` define DMA structures shared with firmware. Exported functions are `snd_mixart_create_pcm`, `snd_mixart_add_ref_pipe`, and `snd_mixart_kill_ref_pipe`.

## Control flow
The header itself has no executable control flow, but its types determine the driver lifecycle. `mixart_mgr` is allocated during PCI probe, `snd_mixart` objects are allocated per logical card, pipes are created lazily when PCM or monitoring paths request them, and streams are attached to ALSA substreams during open. Timer notifications use the bit masks defined here to decode firmware `buffer_id` values into card, PCM, capture/playback, and substream selectors.

## State and persistence behavior
The status macros define stream and pipe state machines. `mgr->dsp_loaded` records which firmware stages have completed. `mgr->sample_rate` and `mgr->ref_count_rate` persist while streams are open. Mixer arrays in `snd_mixart` cache analog, digital, and monitoring control values and are replayed to firmware by mixer update functions. This is all in-memory kernel state for the lifetime of the PCI device.

## Dependencies and integration points
The header depends on Linux interrupt/mutex types and ALSA PCM declarations. It is included by all miXart implementation files and is the contract between ALSA-facing code, firmware setup, IRQ/mailbox processing, and mixer controls.

## Risks and edge cases
Array sizes and notification masks must stay aligned with firmware expectations and descriptor indexing in `mixart.c` and `mixart_core.c`. The fixed `MIXART_MAX_CARDS` value drives card creation, physical connector counts, descriptor allocation, and notification decoding. Changing stream counts or PCM totals requires auditing all index arithmetic.

## Test signals
Compile coverage is the main direct signal for this header. Runtime signals include correct logical-card count, correct notification-to-stream mapping, no out-of-bounds stream selection under timer notifications, and stable mixer defaults across all cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.c -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.c

## Purpose
This file implements the low-level miXart mailbox protocol and interrupt handling. It sends synchronous, notification-waiting, and nonblocking messages to embedded firmware; retrieves responses from firmware message-frame FIFOs; handles outbound doorbell interrupts; processes timer notifications into ALSA period events; enables/disables mailbox interrupts; and resets the board.

## Important APIs, types, and functions
`retrieve_msg_frame` pops posted outbound message-frame addresses from firmware memory. `get_msg` copies a response descriptor and payload out of card memory, performs big-endian conversion on little-endian hosts, and returns the frame to the outbound-free FIFO. `send_msg` obtains an inbound-free frame, writes the message descriptor/data, optionally marks `mgr->pending_event`, and posts the request to firmware.

Public send APIs are `snd_mixart_send_msg`, which blocks for a direct answer; `snd_mixart_send_msg_wait_notif`, which blocks for a specific notification event; and `snd_mixart_send_msg_nonblock`, which posts a request and lets the IRQ thread process the answer. `snd_mixart_interrupt` is the hard IRQ handler that masks interrupts and wakes the threaded handler. `snd_mixart_threaded_irq` drains message frames, dispatches command/notify/answer types, updates stream positions on `MSG_SERVICES_TIMER_NOTIFY`, reports firmware traces, wakes synchronous waiters, and processes queued nonblocking answers. `snd_mixart_init_mailbox`, `snd_mixart_exit_mailbox`, and `snd_mixart_reset_board` manage mailbox registers and reset.

## Control flow
Synchronous sends acquire `msg_lock`, post a frame with a pending answer or notification marker, sleep on `msg_sleep` with a 400 ms timeout, and then retrieve the answer under `msg_lock`. Nonblocking sends post without a pending marker and increment `msg_processed`; when the answer arrives, the IRQ thread queues or immediately processes it through `snd_mixart_process_msg`, then decrements the counter.

The hard IRQ verifies the outbound-doorbell bit, masks mailbox interrupts, clears the doorbell/status registers, and returns `IRQ_WAKE_THREAD`. The threaded handler serializes with `mgr->lock`, repeatedly retrieves message frames, handles firmware commands such as timer notifications and trace reports, wakes pending synchronous waiters for matching answers/notifications, or processes nonblocking answers. At the end it unmasks outbound doorbell interrupts.

Timer notification handling decodes each `buffer_id` into logical card, PCM, capture flag, and substream. For running streams it compares firmware sample count with `abs_period_elapsed`, advances ring-buffer period counters, updates the fragment offset, temporarily drops `mgr->lock`, and calls `snd_pcm_period_elapsed`.

## State and persistence behavior
Mailbox state lives in firmware FIFO pointers in BAR0 memory plus host fields `pending_event`, `msg_sleep`, `msg_fifo`, `msg_fifo_readptr/writeptr`, and `msg_processed`. `mixart_msg_data` is a static shared IRQ scratch buffer protected by `mgr->lock`. Stream pointer state is persisted in each `mixart_stream` until close or trigger reset. No disk persistence exists.

## Dependencies and integration points
This file depends on BAR access macros and register offsets from `mixart_hwdep.h`, message IDs and payload definitions from `mixart_core.h`, driver state from `mixart.h`, Linux threaded IRQ APIs, waitqueues, atomics, mutexes, and ALSA PCM period notification. It is central to all other miXart files because firmware setup, PCM control, clocking, and mixer changes all use its send APIs.

## Risks and edge cases
Message sizes must be 32-bit aligned and within expected response buffers. FIFO pointer validation prevents some corruption, but a bad firmware pointer can still cause protocol failure. The static IRQ scratch buffer means message processing must remain serialized. `snd_mixart_send_msg_nonblock` increments `msg_processed` even when `send_msg` returns an error, which makes callers rely on later drain behavior. Timer notification validation checks card/PCM/substream bounds; malformed capture substream IDs share playback limits and should be reviewed carefully if stream counts change. Missing wakeups or timeout paths can leave firmware and host state out of sync.

## Test signals
Test signals include successful synchronous firmware commands during setup, no 400 ms response timeouts under normal operation, nonblocking start/stop answers decrementing `msg_processed`, period elapsed callbacks driven by timer notifications, trace messages appearing only at debug level, shared IRQ returning `IRQ_NONE` for unrelated interrupts, and clean masking/unmasking around the threaded handler. Fault injection around malformed sizes, empty inbound-free FIFO, and missing notification events is especially useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.h -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.h

## Purpose
This header defines the firmware mailbox protocol contract for miXart. It enumerates message IDs, declares request/response structures exchanged with embedded firmware, defines clock/audio/stream format constants, and exports mailbox, IRQ, and reset functions implemented in `mixart_core.c`.

## Important APIs, types, and functions
`enum mixart_message_id` names connector, console, physical I/O, stream, system, service, and clock messages. `struct mixart_msg` is the generic message envelope used by all send APIs. The many packed structs map directly to firmware payloads: connector enumeration and audio info, streaming group creation/deletion, stream/group start-stop requests, timer notifications, clock properties, stream format parameters, output/input level messages, physical I/O enumeration, and stream level controls.

The exported functions are `snd_mixart_init_mailbox`, `snd_mixart_exit_mailbox`, `snd_mixart_send_msg`, `snd_mixart_send_msg_wait_notif`, `snd_mixart_send_msg_nonblock`, `snd_mixart_interrupt`, `snd_mixart_threaded_irq`, and `snd_mixart_reset_board`.

## Control flow
There is no executable control flow, but the structure definitions drive runtime message flow. Setup uses system and connector messages to enumerate hardware; PCM open/close uses stream group messages; prepare and clock setup use clock and stream-parameter messages; trigger uses stage start/stop messages; mixer controls use physical I/O and stream-level messages; IRQ handling decodes service timer and trace messages.

## State and persistence behavior
The header encodes firmware-visible state rather than owning state directly. Packed payloads preserve binary layout across host/firmware communication. `MIXART_MAX_TIMER_NOTIFY_STREAMS` is derived from `MSG_DEFAULT_SIZE` to keep timer notifications inside the fixed mailbox buffer.

## Dependencies and integration points
It depends on `struct mixart_uid` and constants from `mixart.h` being visible before inclusion in implementation files. It is included by main, core, firmware, and mixer sources and is the shared ABI with firmware.

## Risks and edge cases
Because structs are packed firmware ABI, changing field order, width, signedness, or maximum counts can break hardware communication. Endianness is handled in mailbox copy paths, so every payload must remain composed of 32-bit-aligned firmware words unless the copy logic changes. The timer-notification size calculation protects the default mailbox buffer and should be rechecked if stream structures grow.

## Test signals
Build tests catch missing declarations; runtime tests should exercise every message family: firmware enumeration, stream creation/deletion, clock setting, format setting, stage start/stop, timer notifications, and mixer level updates. Cross-endian builds are important because payload byte-swapping depends on these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.c -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.c

## Purpose
This file manages miXart firmware loading and first hardware discovery. It requests and stages motherboard Xilinx, motherboard ELF, and optional AES daughterboard Xilinx firmware; synchronizes with firmware pseudo-register status values; passes the flow table address to the embedded system; initializes the mailbox; enumerates connectors and physical I/O UIDs; creates PCM/mixer devices after firmware is ready; and registers ALSA cards.

## Important APIs, types, and functions
`mixart_wait_nice_for_register_value` polls pseudo-registers with timeout and `cond_resched`. `mixart_load_elf` parses a big-endian ELF32 firmware image and copies loadable program segments into BAR0 memory. `mixart_enum_connectors` sends play and record connector enumeration messages and stores left/right connector UIDs in each card's analog/digital pipes. `mixart_enum_physio` obtains the console manager UID and physical analog I/O UIDs. `mixart_first_init` runs connector/physical enumeration and sends an initial synchronization command.

`mixart_dsp_load` is the staged firmware loader for `MIXART_MOTHERBOARD_XLX_INDEX`, `MIXART_MOTHERBOARD_ELF_INDEX`, and `MIXART_AESEBUBOARD_XLX_INDEX`. `snd_mixart_setup_firmware` requests `mixart/miXart8.xlx`, `mixart/miXart8.elf`, and `mixart/miXart8AES.xlx`, feeds them through `mixart_dsp_load`, releases each firmware object, and records `mgr->dsp_loaded` bits.

## Control flow
Firmware setup always iterates through the three firmware filenames. The motherboard Xilinx stage checks idle/already-loaded status, validates word alignment and sentinel content, writes base and size pseudo-registers, copies the image to the hard-coded BAR0 address, and marks copy finished. The ELF stage waits for Xilinx started status, resets board number and flow-table pointer, parses/copies ELF segments, marks ELF copy complete, waits for started status, and writes the host flowinfo DMA address to `MIXART_FLOWTABLE_PTR`.

The daughterboard stage waits for ELF and motherboard Xilinx readiness, waits for daughterboard presence, reads `mgr->board_type`, skips image transfer if no daughterboard exists, rejects non-AES daughterboards, coordinates size/status/base-address pseudo-registers for AES Xilinx transfer, and then waits for daughter initialization. After that, it initializes the mailbox, performs first firmware enumeration, creates PCMs for every logical card, creates the mixer once for the manager, and registers all cards.

## State and persistence behavior
Firmware progress is tracked by pseudo-register values in BAR0 and by host `mgr->dsp_loaded` bits. `mgr->board_type`, `mgr->uid_console_manager`, per-pipe connector UIDs, and per-card physical I/O UIDs are discovered after ELF startup and persist for the manager lifetime. The flow table pointer given to firmware points at a host DMA allocation created by `mixart.c`.

## Dependencies and integration points
This file depends on the Linux firmware loader, BAR memory access macros and pseudo-register offsets from `mixart_hwdep.h`, mailbox send APIs from `mixart_core.c`, message structures from `mixart_core.h`, PCM creation from `mixart.c`, and mixer creation from `mixart_mixer.c`. Firmware names are also declared through `MODULE_FIRMWARE`.

## Risks and edge cases
Firmware loading is order-sensitive and timeout-sensitive. Missing any firmware file fails setup, even when no AES daughterboard is present because the loop still requests the AES image before `mixart_dsp_load` can skip transfer. ELF parsing trusts firmware headers enough to copy program segments to BAR0 offsets; invalid firmware can fail or corrupt device memory. Pseudo-register status values are magic constants with limited validation. The physical I/O enumeration assumes at least two analog I/O UIDs per card and specific ordering between input and output halves.

## Test signals
High-value signals include firmware request success/failure paths, status transitions for Xilinx/ELF/daughter stages, correct detection of no daughterboard versus AES daughterboard, connector UID assignment for all cards, physical I/O UID assignment, card registration only after firmware setup, and cleanup on failures at each firmware stage. Logs such as "xilinx load error", "elf could not be started", "daughter board load error", and "miXart could not be set up" identify stage-specific failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.h -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.h

## Purpose
This header defines low-level miXart hardware access helpers and register layout. It provides endian-aware MMIO read/write macros, BAR address helpers, daughterboard type constants, BAR sizes, pseudo-register offsets for firmware loading and performance counters, mailbox FIFO addresses, message-frame layout constants, interrupt register offsets/masks, reset offset, and the firmware setup function prototype.

## Important APIs, types, and functions
`readl_be`, `writel_be`, `readl_le`, and `writel_le` normalize MMIO endianness where architecture helpers are absent. `MIXART_MEM(mgr, x)` addresses BAR0 memory and `MIXART_REG(mgr, x)` addresses BAR1 registers. Constants under `MIXART_PSEUDOREG_*` coordinate firmware status, base addresses, board type, daughterboard presence, flow-table pointer, and performance counters. `MSG_*` constants describe firmware mailbox FIFO pointers, stacks, frame sizes, and resource-protection words. `MIXART_PCI_*` constants describe interrupt mask/status/doorbell registers. The exported declaration is `snd_mixart_setup_firmware`.

## Control flow
The header has no executable control flow, but its offsets drive firmware loading, mailbox initialization, message send/receive, interrupt masking/unmasking, proc BAR reads, and board reset. `mixart_hwdep.c` uses pseudo-register constants during firmware staging; `mixart_core.c` uses mailbox and interrupt constants; `mixart.c` uses BAR sizes for proc entries.

## State and persistence behavior
The constants define hardware and firmware state locations. Firmware status pseudo-registers persist while the board is powered. Mailbox head/tail registers represent shared host/firmware queue state. The brutal reset offset is used during teardown when firmware had been loaded.

## Dependencies and integration points
It depends on ALSA hwdep declarations and Linux raw MMIO/endian helpers. All miXart implementation files include it either directly or indirectly for BAR and protocol access.

## Risks and edge cases
Incorrect offsets or endian accessors can break firmware loading or mailbox traffic immediately. Pointer arithmetic assumes valid `mgr->mem[0].virt` and `mgr->mem[1].virt` mappings. The mailbox stack and frame constants must match embedded firmware exactly. The daughterboard masks drive feature decisions; wrong values can expose unsupported digital devices or reject valid hardware.

## Test signals
Compile tests on little- and big-endian targets are useful for accessor coverage. Runtime signals include successful BAR proc reads, correct firmware stage status polling, mailbox message exchange, interrupt delivery through OIDI, and board reset during driver removal after firmware load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.c

## Purpose
This file implements ALSA mixer controls for miXart analog output/input, digital PCM/AES stream levels, playback switches, and analog monitoring. It maintains cached control values in `struct snd_mixart`, converts ALSA integer controls into firmware float encodings, sends mailbox level-update messages, and creates the mixer controls for every logical card after firmware setup.

## Important APIs, types, and functions
`mixart_analog_level` and `mixart_digital_level` are 256-entry lookup tables of firmware float values for dB-scaled analog and digital levels. `mixart_update_analog_audio_level` sends `MSG_PHYSICALIO_SET_LEVEL` to analog physical I/O. `mixart_update_playback_stream_level` sends `MSG_STREAM_SET_OUT_STREAM_LEVEL` for analog or AES playback streams. `mixart_update_capture_stream_level` sends `MSG_STREAM_SET_IN_AUDIO_LEVEL` for analog or AES capture connectors. `mixart_update_monitoring` sends `MSG_CONNECTOR_SET_OUT_AUDIO_LEVEL` for monitoring paths.

ALSA control callbacks include analog volume get/put/info, master playback switch get/put, digital PCM/AES volume get/put/info, PCM/AES playback switch get/put, monitoring volume get/put, and monitoring switch get/put. `mixart_reset_audio_levels` programs initial analog levels. `snd_mixart_create_mixer` creates all relevant controls for every logical card and conditionally adds AES controls when the board type is AES.

## Control flow
Mixer creation initializes `mgr->mixer_mutex`, iterates over all logical cards, adds master playback volume/switch controls, adds capture volume only on the first two cards, adds PCM playback/capture volume controls, conditionally adds AES playback/capture volume and switch controls, adds monitoring controls, and pushes initial analog levels to firmware.

Control `get` callbacks return cached values under `mixer_mutex`. `put` callbacks validate ranges, update cached values, and when changed call the corresponding firmware update helper. Playback stream updates are no-ops until the relevant pipe exists. Monitoring switch changes allocate analog playback and capture pipes for monitoring when either channel is active, update changed monitoring channels, and release monitoring pipe references when both channels are disabled.

## State and persistence behavior
The persistent mixer state is the set of cached arrays in `struct snd_mixart`: analog playback active/volume, analog capture volume, digital playback active/volume, digital capture volume, and monitoring active/volume. This state lives for the ALSA card lifetime and is replayed to firmware as controls change or streams configure. It is not stored on disk by the driver; user-space ALSA state tools may persist controls externally.

## Dependencies and integration points
This file depends on ALSA control and TLV APIs, the mailbox send API, firmware message structures, pipe state from `mixart.h`, and hardware constants from `mixart_hwdep.h`. PCM setup in `mixart.c` calls the exported playback/capture stream-level update functions during `hw_params`, and firmware setup calls `snd_mixart_create_mixer`.

## Risks and edge cases
The volume lookup tables and min/max/zero constants must remain aligned with the ALSA TLV scales and firmware semantics. Some invalid user values are silently ignored rather than returning errors. `mixart_monitor_vol_put` coerces assigned volume with `!!`, which collapses values to 0 or 1 before sending a digital-level table index and may be unintended for a volume control. Monitoring pipe allocation errors are not strongly propagated through the switch path. AES controls must only appear when firmware detected an AES daughterboard.

## Test signals
Tests should verify control enumeration and names on analog-only and AES boards, TLV ranges, get/put round trips, firmware messages emitted on changed values only, no firmware update when a pipe is undefined for stream controls, monitoring pipe allocation/release behavior, and initial master level programming. Boundary tests for min/max volume indices and invalid values are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.h -->
# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.h

## Purpose
This small header declares the mixer interface exported by `mixart_mixer.c` to the rest of the miXart driver.

## Important APIs, types, and functions
It declares `mixart_update_playback_stream_level`, `mixart_update_capture_stream_level`, and `snd_mixart_create_mixer`. The first two are used by PCM hardware-parameter setup to push cached stream levels once stream format/buffer setup occurs. The third creates ALSA controls and initializes hardware-visible levels after firmware setup.

## Control flow
The header has no runtime control flow. It enables `mixart.c` and `mixart_hwdep.c` to call mixer routines without depending on mixer implementation details.

## State and persistence behavior
No state is stored here. The declarations operate on `struct snd_mixart` and `struct mixart_mgr` state defined in `mixart.h`.

## Dependencies and integration points
The prototypes require the driver-visible `struct snd_mixart` and `struct mixart_mgr` declarations from `mixart.h` in including translation units. It is included by `mixart.c`, `mixart_hwdep.c`, and `mixart_mixer.c`.

## Risks and edge cases
Signature drift between this header and the implementation would break the module build. Because these functions are cross-file integration points, changes to mixer locking or pipe assumptions need coordinated updates in PCM and firmware setup code.

## Test signals
Successful `snd-mixart` build is the direct signal. Runtime signals are covered by PCM `hw_params` stream-level updates and mixer creation after firmware setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/nm256/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/nm256/Makefile

## Purpose
This Kbuild file defines the ALSA NeoMagic NM256 PCI audio driver module.

## Important APIs, types, and functions
`snd-nm256-y := nm256.o` states that the module is built from `nm256.o`. `obj-$(CONFIG_SND_NM256) += snd-nm256.o` links the module when `CONFIG_SND_NM256` is enabled.

## Control flow
There is no runtime control flow. Kbuild consumes this file to compile and link the NM256 ALSA PCI module according to kernel configuration.

## State and persistence behavior
There is no runtime or persistent state. The file only records static build composition.

## Dependencies and integration points
It depends on the kernel Kbuild system and `CONFIG_SND_NM256`. It integrates the local `nm256.c` implementation into the ALSA PCI build.

## Risks and edge cases
The build will omit the NM256 driver if the config symbol is disabled. If the implementation is split into more objects, this Makefile must be updated or symbols will be missing.

## Test signals
Build with `CONFIG_SND_NM256=m` or `=y` should produce `snd-nm256`; disabling the symbol should omit it. A module link with no unresolved symbols validates the object list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/nm256/Makefile -->

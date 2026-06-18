# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.h

## Purpose

This is the main shared header for the PCXHR driver. It defines driver version constants, stream/pipe/card limits, clock-type enums, the manager/card/stream/pipe state structures, and the top-level exported functions used across implementation files.

## Important APIs, Types, And Functions

- `enum pcxhr_clock_type` defines generic PCXHR clock sources and HR22 aliases.
- `struct pcxhr_mgr` models a physical PCI board and owns shared device state such as ports, IRQ, mutexes, firmware status, board capability flags, clock/timer values, async error counters, cached Xilinx/DSP register copies, and logical card pointers.
- `enum pcxhr_stream_status` and `struct pcxhr_stream` describe PCM stream lifecycle and timer-derived pointer accounting.
- `struct pcxhr_pipe` tracks DSP pipe definition, direction, and first audio index.
- `struct snd_pcxhr` models one logical ALSA card and stores PCM devices, pipes, streams, mixer cache, mic/phantom state, and IEC958 bits.
- Export declarations include `pcxhr_create_pcm()`, `pcxhr_set_clock()`, and `pcxhr_get_external_clock()`.

## Control Flow

The header does not execute code, but its structures define the control-flow contracts used by the rest of the module. `pcxhr.c` owns most `pcxhr_stream_status` transitions, `pcxhr_hwdep.c` defines pipes and firmware state, `pcxhr_core.c` updates timer/async state, and `pcxhr_mixer.c`/`pcxhr_mix22.c` update mixer caches and board-specific register copies.

## State And Persistence

All significant runtime state is declared here. Locks are split by purpose: `lock` protects interrupt/timer stream state, `msg_lock` serializes DSP command transport, `setup_mutex` coordinates open/close/hw_params/clock setup, and `mixer_mutex` protects ALSA control caches. The state is memory-only and rebuilt on probe.

## Dependencies And Integration Points

The header depends on Linux interrupt/mutex types and ALSA PCM types. It is included by all PCXHR implementation files, so changes here affect module-wide ABI between objects.

## Risks

- Bit-field capability flags in `pcxhr_mgr` must match board discovery and board-parameter logic.
- Array dimensions (`PCXHR_MAX_CARDS`, `PCXHR_PLAYBACK_STREAMS`, two capture streams) are assumed in loops across multiple files.
- Stream status enum changes require synchronized updates in trigger, close, IRQ timer update, and DSP start/stop paths.
- The manager lock split must be preserved to avoid sleeping in interrupt-sensitive sections or racing DSP command traffic.

## Test Signals

Compilation is the first signal for structural changes. Runtime validation should stress multi-card boards, stream state transitions, mixer control state, and interrupt pointer accounting because all of those rely on structures declared here.

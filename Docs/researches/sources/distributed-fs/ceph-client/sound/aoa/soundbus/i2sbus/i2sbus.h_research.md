# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/i2sbus.h

## Purpose
This private header defines the shared data model and internal API contracts for the Apple I2S soundbus implementation. It ties together the macio registration layer, DBDMA descriptor management, PCM operations, interrupt handlers, and platform control functions.

## Important APIs, Types, And Functions
`struct i2sbus_control` owns the per-macio controller list and macio chip pointer. `struct dbdma_command_mem` records coherent command memory, aligned command start, bus addresses, size, and `running`/`stopping` flags. `struct pcm_info` tracks one playback or capture direction, including ALSA substream, current period, frame counter, DBDMA ring, DBDMA register block, and optional stop completion. `struct i2sbus_dev` embeds `struct soundbus_dev` and contains all hardware, resource, stream, clock, and locking state. The header declares PCM callbacks (`i2sbus_attach_codec()`, IRQ handlers, wait/prepare helpers) and control-layer callbacks (`i2sbus_control_init()`, add/remove, enable, cell, clock).

## Control Flow
The header itself has no executable flow, but it defines how the implementation is partitioned. `core.c` allocates and initializes `i2sbus_dev`, `pcm.c` consumes `pcm_info` and DBDMA fields, and the control implementation supplies platform power/clock callbacks stored in the device.

## State And Persistence
State is intentionally split by granularity: controller-wide list state in `i2sbus_control`, per-direction stream and DBDMA state in `pcm_info`, and per-bus hardware/power state in `i2sbus_dev`. `low_lock` protects interrupt-level state such as DBDMA flags and period indexes; `lock` protects high-level stream and codec consistency.

## Dependencies And Integration Points
The header includes Linux interrupt/spinlock/mutex/completion primitives, ALSA PCM types, Apple PMAC feature and DBDMA headers, local register definitions from `interface.h`, and generic AOA soundbus definitions. Its declared functions are the internal ABI between the I2S bus registration, control, and PCM compilation units.

## Risks And Test Signals
Because the header exposes bitfields shared between process and IRQ contexts, races around `running`, `stopping`, `active`, and `substream` ownership are key risk areas. Build testing should cover both PM and non-PM configurations because `i2sbus_wait_for_stop_both()` and `i2sbus_pcm_prepare_both()` are PM-only declarations. Runtime testing should verify that DBDMA rings are sized for `MAX_DBDMA_COMMANDS` and that playback/capture state transitions remain consistent under duplex use.

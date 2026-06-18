# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/base.c

## Purpose
Implements the common SEC2 engine lifecycle. SEC2 is a falcon-based security processor used for ACR and low-secure falcon bootstrapping on newer NVIDIA GPUs.

## Important APIs, types, and functions
`nvkm_sec2_new_()` allocates `struct nvkm_sec2`, loads a firmware interface with `nvkm_firmware_load()`, constructs the falcon, and creates a queue manager plus command/message queues. Engine callbacks include `nvkm_sec2_oneinit()`, `nvkm_sec2_init()`, `nvkm_sec2_fini()`, and `nvkm_sec2_dtor()`. `nvkm_sec2_finimsg()` handles unload completion.

## Control flow, state, and persistence
Initialization acquires the falcon, clears interrupts, resets `initmsg` and `running`, enables the interrupt handler, and starts firmware. Oneinit registers the SEC2 interrupt, optionally through a generation-specific vector provider. Fini sends an unload command if firmware initialized queues, waits for halt, blocks interrupts, tears down queues, disables falcon, and releases ownership. State is kept in atomics, falcon state, and queue objects.

## Dependencies and integration points
Depends on falcon queue helpers, `nvfw/sec2.h`, firmware loader, MC interrupts, and timer polling. ACR code uses SEC2 command queues for bootstrap commands.

## Risks and test signals
Init-message parsing gates queue readiness. Interrupt blocking and unload timeouts are sensitive during suspend/resume. Signals include init message success, command queue ready completion, unload warnings, halt logs, and successful ACR bootstrap.

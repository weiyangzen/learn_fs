# sources/distributed-fs/ceph-client/include/linux/mfd/loongson-se.h

Purpose: This header defines the Loongson Security Engine MFD interface for controller commands, interrupts, engine IDs, command sizes, and per-engine runtime state.

Important APIs, types, and functions: Macros define controller command timeout, command registers, command IDs for start/DMA/engine command buffer setup, interrupt status/enable/clear/set registers, all/controller interrupt masks, maximum engine count, RNG and TPM engine IDs and command bases, and command buffer size. `struct loongson_se_engine` stores the parent security engine pointer, engine ID, command and return buffers, data buffer, buffer size and DMA-base offset, and completion. Exported functions are `loongson_se_init_engine` and `loongson_se_send_engine_cmd`.

Control flow, state, and persistence: Consumers initialize a selected engine, prepare command/data buffers, send an engine command through controller registers, and wait on completion signaled by interrupts. State includes DMA command/data buffers, per-engine completion, interrupt status, and engine command return contents.

Dependencies and integration points: It integrates with Loongson SE parent code, DMA-capable buffers, completion/interrupt handling, RNG and TPM child drivers, and MMIO register access.

Risks and test signals: Risks include command timeout, DMA offset/size mismatch, completion not firing on interrupt loss, command buffer alignment assumptions, and engine ID misuse. Test signals include RNG command smoke tests, TPM command exchange, interrupt clear/enable tests, timeout/error injection, and DMA buffer boundary checks.

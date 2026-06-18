# sources/distributed-fs/ceph-client/drivers/misc/dummy-irq.c

Purpose: provides a diagnostic module that registers a shared dummy interrupt handler for a user-specified IRQ to help debug spurious interrupts on disabled vectors.

Important APIs, types, and functions: module parameter `irq` is declared with `module_param_hw()`. `dummy_irq_init()` validates and registers the IRQ; `dummy_irq_exit()` frees it. `dummy_interrupt()` logs the first interrupt occurrence and always returns `IRQ_NONE`.

Control flow: module load fails unless `irq=N` is provided and `request_irq()` succeeds. Once loaded, the shared handler observes interrupts but deliberately does not claim them. Module unload frees the same dev_id pointer used at registration.

State and persistence: the only driver state is global `irq` and a static `count` inside the handler that suppresses repeated informational logs. No persistent state.

Dependencies and integration points: depends on Linux interrupt APIs and module parameter infrastructure. It is standalone and does not bind to hardware devices.

Risks: registering on the wrong IRQ can add overhead to a real interrupt line. Returning `IRQ_NONE` is intentional but can still contribute to spurious IRQ accounting. The handler's static `count` is not atomic, but it only gates a best-effort one-time log.

Test signals: load without `irq` should fail, load with an invalid/busy IRQ should fail, load with a shared IRQ should register, first interrupt should log once, and unload should free the handler cleanly.

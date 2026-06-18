# sources/distributed-fs/ceph-client/include/linux/scx200_gpio.h

Purpose: `scx200_gpio.h` provides inline GPIO accessors and shared state declarations for the SCx200 GPIO block. It is performance-oriented legacy I/O code that updates shadow output registers and writes them to the hardware port.

Important APIs/types/functions: Exports include `scx200_gpio_configure()`, `scx200_gpio_base`, `scx200_gpio_shadow[2]`, `scx200_gpio_ops`, and `scx200_gpio_present()`. Inline operations are `scx200_gpio_get()`, `scx200_gpio_current()`, `scx200_gpio_set_high()`, `scx200_gpio_set_low()`, `scx200_gpio_set()`, and `scx200_gpio_change()`. Internal macros compute bank, I/O address, shadow pointer, masked index, and the `outsl` write.

Control flow: Callers compute a GPIO bank from `index >> 5`, reduce the index to a bank-local bit, update or read `scx200_gpio_shadow`, and perform port I/O. Input reads add `0x04` to the bank I/O address and test the selected bit.

State and persistence behavior: Output state is mirrored in the global `scx200_gpio_shadow` array and pushed to hardware via `outsl`. The current electrical input state is read from hardware, while `scx200_gpio_current()` reports the shadowed drive value. Configuration changes are delegated to `scx200_gpio_configure()`.

Dependencies and integration points: It depends on x86 I/O helpers, bit operations, and `struct nsc_gpio_ops` from the NSC GPIO subsystem. It integrates with legacy GPIO clients and board support using direct I/O port access.

Risks: Shadow updates are not visibly locked here; concurrent writers can race unless implementation-level locking wraps calls. The inline assembly constraint and direct `outsl` assume the platform I/O model. Invalid indexes can select unexpected banks because no bounds check exists.

Test signals: Exercise absent hardware fallback, GPIO input reads, output high/low/toggle, concurrent updates to different pins in the same bank, configuration changes, and shadow/hardware consistency after repeated writes.

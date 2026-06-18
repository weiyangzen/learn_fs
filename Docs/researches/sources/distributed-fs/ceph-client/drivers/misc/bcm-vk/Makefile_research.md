# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Makefile

Purpose: defines the object composition for the Broadcom VK accelerator driver.

Important APIs and entries: `obj-$(CONFIG_BCM_VK)` builds `bcm_vk.o`. The base object links `bcm_vk_dev.o`, `bcm_vk_msg.o`, and `bcm_vk_sg.o`. `bcm_vk-$(CONFIG_BCM_VK_TTY)` conditionally adds `bcm_vk_tty.o`.

Control flow: kbuild combines PCI lifecycle/firmware loading, message queues, scatter-gather DMA, and optional tty support into one module or built-in object.

State and persistence: no runtime state; build composition determines whether tty functions are real implementations or inline stubs from `bcm_vk.h`.

Dependencies and integration points: depends on Kconfig symbols in the same directory and on internal headers shared by device, message, scatter-gather, and tty code.

Risks: adding new driver subsystems requires updating the object list. Conditional tty linkage must stay synchronized with the stubs and IRQ count macros in `bcm_vk.h`.

Test signals: base-only and tty-enabled builds, link checks for internal symbols, and module load tests confirming expected device nodes.

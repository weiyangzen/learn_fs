# sources/distributed-fs/ceph-client/drivers/irqchip/irq-al-fic.c

Purpose: Implements Amazon/Annapurna Labs Fabric Interrupt Controller wire-mode support as a 32-source cascaded irqchip.

Important APIs/types/functions: `struct al_fic`, `enum al_fic_state`, `al_fic_irq_set_type()`, `al_fic_irq_handler()`, `al_fic_irq_retrigger()`, `al_fic_register()`, `al_fic_wire_init()`, and `al_fic_init_dt()`.

Control flow: DT init maps MMIO, maps the parent IRQ, initializes hardware with all sources masked and cause cleared, creates a linear domain with generic chips, configures mask/ack registers and callbacks, and installs a chained parent handler. The first child interrupt type selection configures the whole FIC as level-high or rising-edge; later attempts to use a different mode are rejected.

State and persistence: `struct al_fic` stores base, domain, name, parent IRQ, and trigger state. Generic chip mask cache tracks masked sources. Hardware state includes cause, mask, control trigger mode, and MSI-X masking.

Dependencies/integration: Uses OF mapping, irqdomain generic chips, chained IRQ helpers, bitfield helpers, and generic mask/ack operations.

Risks and test signals: Test mixed trigger requests, retrigger via set-cause register, mask-cache correctness, parent IRQ disposal on init failure, and level/edge handler switching after the first configured source.

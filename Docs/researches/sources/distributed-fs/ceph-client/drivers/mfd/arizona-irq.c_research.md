<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c

Purpose: implements interrupt support for Arizona-class codecs. It maps the physical IRQ line into a two-entry virtual IRQ domain for always-on and main interrupt domains, attaches variant-specific regmap IRQ chips, exposes child-facing IRQ request/free/wake helpers, and handles top-level threaded dispatch with runtime PM.

Important APIs and functions: exported APIs are `arizona_request_irq`, `arizona_free_irq`, `arizona_set_irq_wake`, `arizona_irq_init`, and `arizona_irq_exit`. Key internals are `arizona_map_irq`, `arizona_irq_thread`, `arizona_irq_map`, `arizona_boot_done`, and `arizona_ctrlif_err`.

Control flow: initialization chooses AOD and main regmap IRQ chips based on codec type and revision, disables wake sources, derives IRQ trigger flags if platform data did not specify them, configures IRQ polarity, creates a linear IRQ domain with AOD and main mappings, attaches regmap IRQ chips, optionally translates legacy GPIO IRQs, requests the physical threaded IRQ, and requests core boot-done/control-interface-error nested IRQs. The top-level thread runtime-resumes the codec, checks AOD status, dispatches the AOD nested IRQ when needed, checks main IRQ pin status, dispatches main nested IRQ, optionally polls GPIO pin level for legacy edge emulation, and runtime-autosuspends.

State and persistence: state is stored in `struct arizona`: physical IRQ, virtual IRQ domain, regmap IRQ chip data pointers, `ctrlif_error`, platform IRQ flags, and optional legacy IRQ GPIO. Hardware interrupt masks/status are managed through regmap IRQ chips.

Dependencies and integration points: depends on regmap IRQ, Linux IRQ domains, nested threaded IRQs, runtime PM, optional legacy GPIO, and variant IRQ chip tables declared in `arizona.h`. Child drivers use the exported helper APIs with Arizona logical IRQ numbers instead of directly touching regmap IRQ data.

Risks: teardown always calls `regmap_del_irq_chip` for AOD mapping even when `aod_irq_chip` is NULL; this relies on safe NULL behavior in surrounding paths and mappings. The default branch uses a `BUG_ON("Unknown Arizona class device" == NULL)` expression that is intentionally false and then returns `-EINVAL`, which is unusual. Runtime resume failure in the top-level IRQ returns `IRQ_NONE`, which can matter for shared IRQ diagnostics. IRQ polarity corrections must match board wiring, especially ACPI SPI boards fixed in `arizona-spi.c`.

Test signals: nested IRQ delivery for AOD and main domains, boot-done IRQ unmasking across resume, wake-source control via `arizona_set_irq_wake`, variant/revision IRQ chip selection, active-low and active-high IRQ polarity, legacy GPIO polling behavior, runtime PM interaction during IRQ storms, and clean teardown on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c

Purpose: Adds Lemote 2F suspend wakeup behavior for keyboard and Yeeloong EC lid SCI events.

Important APIs/types/functions: `setup_wakeup_events()`, `wakeup_loongson()`, weak `mach_suspend()`/`mach_resume()` overriding common defaults, `i8042_enable_kbd_port()`, delayed lid work, and exported `yeeloong_report_lid_status`.

Control flow: Netbook machtypes unmask keyboard and SCI IRQs, enable the i8042 keyboard port, and during wake polling query the actual i8259 IRQ. Keyboard IRQ wakes immediately; SCI IRQ queries EC event number and only wakes on lid-open status, scheduling delayed lid reporting after resume.

State and persistence: Caches i8042 control byte, lazily initializes delayed work, and toggles MFGPT0 counter across suspend/resume.

Dependencies and integration: Uses `mach_i8259_irq()`, EC accessors, i8042 core, PIC registers, and common PM weak hooks.

Risks: Scheduling work from suspend path is delayed deliberately but depends on `initialized` race avoidance. EC or i8042 command timeouts can prevent wake. Only selected machtypes configure wake sources.

Test signals: On Yeeloong/Mengloong, keyboard and lid-open should wake from suspend; MFGPT0 should be disabled during suspend and reenabled on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c -->

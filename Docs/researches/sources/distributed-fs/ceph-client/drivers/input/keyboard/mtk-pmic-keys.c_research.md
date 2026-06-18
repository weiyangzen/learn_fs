## sources/distributed-fs/ceph-client/drivers/input/keyboard/mtk-pmic-keys.c

Purpose: MediaTek PMIC power/home key driver for MT6397, MT6323, MT6331, MT6357, MT6358, and MT6359 families. It reports PMIC debounced key state and configures optional long-press reset behavior.

Important APIs/types/functions: `struct mtk_pmic_regs` provides per-chip register layouts; `struct mtk_pmic_keys_info` stores per-key registers, keycode, IRQs, and wake flag; `struct mtk_pmic_keys` stores input, device, regmap, and two key slots. `mtk_pmic_key_setup()` configures interrupt selection and IRQs. `mtk_pmic_keys_irq_handler_thread()` reads the debounce register and reports key state. `mtk_pmic_keys_lp_reset_setup()` programs long-press reset mode.

Control flow: probe gets the parent `mt6397_chip` regmap, matches chip data, allocates input, iterates child key nodes in fixed power/home order, gets named IRQs and optional release IRQs, reads `linux,keycodes`, sets wake flags, requests IRQs, registers input, then programs long-press reset. Suspend/resume enable or disable IRQ wake for per-key wake sources.

State/dependencies/integration: state is per-key metadata and PMIC registers. Dependencies are MFD register headers, parent regmap, OF child nodes, platform named IRQs, input core, and PM.

Risks and test signals: child iteration order must match fixed `powerkey`/`homekey` arrays. Some chip data differs in release IRQ support. The MT6357 home reset mask entry uses `MTK_PMIC_HOMEKEY_INDEX`, which deserves validation against hardware definitions. Test all compatible tables, one-key/two-key reset modes, press and release IRQ variants, wakeup-source handling, and missing child properties.

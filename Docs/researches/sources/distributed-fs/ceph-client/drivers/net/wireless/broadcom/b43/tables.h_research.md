# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.h

`tables.h` declares shared PHY lookup tables exported by `tables.c` and defines their expected lengths for compile-time checks and caller loop bounds.

Important constants include `B43_TAB_ROTOR_SIZE`, `B43_TAB_RETARD_SIZE`, `B43_TAB_FINEFREQA_SIZE`, `B43_TAB_FINEFREQG_SIZE`, `B43_TAB_NOISE*` sizes, `B43_TAB_NOISESCALE_SIZE`, `B43_TAB_SIGMASQR_SIZE`, `B43_TAB_RSSIAGC1_SIZE`, and `B43_TAB_RSSIAGC2_SIZE`. Extern declarations cover `b43_tab_rotor`, `b43_tab_retard`, fine-frequency arrays, noise arrays, noise-scale arrays, sigma-square arrays, and RSSI AGC arrays.

There is no executable logic or state. The header is included by `tables.c` and callers such as `wa.c`, which loop over the arrays using these size macros while applying PHY workarounds.

Risks are mostly contract drift: size macros must exactly match the array definitions. `tables.c` catches mismatches with `BUILD_BUG_ON()` when built. Test signals include G-PHY/b43 build coverage and review that callers use the macros rather than hard-coded lengths.

# sources/distributed-fs/ceph-client/drivers/usb/chipidea/otg_fsm.h

Purpose: defines OTG FSM timing constants for ChipIdea and declares the conditional FSM integration API.

Important APIs/types/functions: constants include `TA_WAIT_VRISE`, `TA_WAIT_VFALL`, `TA_WAIT_BCON`, `TA_AIDL_BDIS`, `TA_BIDL_ADIS`, `TB_DATA_PLS`, `TB_SRP_FAIL`, `TB_ASE0_BRST`, `TB_SE0_SRP`, `TB_SSEND_SRP`, and `TB_AIDL_BDIS`. Declares or stubs `ci_hdrc_otg_fsm_init`, `ci_otg_fsm_work`, `ci_otg_fsm_irq`, `ci_hdrc_otg_fsm_start`, and `ci_hdrc_otg_fsm_remove`.

Control flow: no direct runtime flow except inline stubs when `CONFIG_USB_OTG_FSM` is disabled.

State and persistence: no owned state; constants drive hrtimer scheduling in `otg_fsm.c`.

Dependencies and integration: includes Linux `usb/otg-fsm.h` and is used by core and OTG code to conditionally include FSM behavior.

Risks: timing constants encode USB OTG specification assumptions; changes can affect compliance. Disabled-FSM stubs return success for init but `-ENXIO` for work, so callers must only enter work path when `ci_otg_is_fsm_mode` is true.

Test signals: build with and without `CONFIG_USB_OTG_FSM`, plus OTG SRP/HNP timer compliance tests.

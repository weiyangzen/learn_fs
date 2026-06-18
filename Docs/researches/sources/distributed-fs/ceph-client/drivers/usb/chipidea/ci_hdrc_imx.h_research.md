# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.h

Purpose: declares the i.MX USBMISC data contract and helper APIs used by the i.MX ChipIdea glue driver.

Important APIs/types/functions: defines `struct imx_usbmisc_data` with device/index, over-current polarity, power polarity, external VBUS divider, ULPI/HSIC flags, external ID/VBUS flags, USB PHY, available role, and PHY tuning values. Declares `imx_usbmisc_init`, `imx_usbmisc_init_post`, `imx_usbmisc_hsic_set_connect`, `imx_usbmisc_charger_detection`, `imx_usbmisc_suspend`, `imx_usbmisc_resume`, and `imx_usbmisc_pullup`.

Control flow: no executable flow. The header supplies the typed interface between `ci_hdrc_imx.c` and USBMISC implementation files.

State and persistence: `imx_usbmisc_data` persists SoC-specific sideband configuration and is stored by the glue driver for notifications and PM.

Dependencies and integration: depends on USB PHY and USB role mode types through included users. It is included by both ChipIdea i.MX glue and USBMISC code.

Risks: bitfield names such as external ID/VBUS control hardware behavior indirectly; stale or incorrectly parsed data-tree properties can cause wrong wakeup, charger, or over-current behavior.

Test signals: compile with i.MX glue and USBMISC, validate DT parsing populates fields, and exercise USBMISC init/post/suspend/resume plus charger and pullup notifications.

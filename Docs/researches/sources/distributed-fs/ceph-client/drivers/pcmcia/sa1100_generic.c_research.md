# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.c

Purpose: Registers SA-11x0 PCMCIA platform support for both legacy machine-specific sockets and newer GPIO/regulator-described CF sockets.

Important APIs and functions: `sa11x0_cf_hw_init()` obtains reset, optional bus-enable, optional Vcc regulator, and status GPIOs. `sa11x0_cf_configure_socket()` applies Vcc through `soc_pcmcia_regulator_set()`. `sa11x0_drv_pcmcia_probe()` chooses legacy init for platform id `-1` or creates one socket using `sa11xx_drv_pcmcia_add_one()`. Remove paths call `soc_pcmcia_remove_one()`.

Control flow: Modern probe allocates a `soc_pcmcia_socket`, gets the clock, installs SA11xx timing callbacks into `sa11x0_cf_ops`, initializes the common socket, and registers it. Legacy probe iterates machine-specific init functions built by config, stopping at the first successful match.

State and persistence: Modern socket state includes GPIO descriptors, regulator state, clock, and common SoC socket state. Legacy state is stored in the `skt_dev_info` set by machine-specific init. Hardware power/reset state persists through GPIO and regulator outputs.

Dependencies and integration points: Depends on `soc_common.c`, `sa11xx_base.c`, Linux platform/GPIO/regulator APIs, and optional machine-specific functions such as H3600 and Collie.

Risks: Optional regulator handling returns `PTR_ERR()` for all `IS_ERR()` values; behavior depends on how optional regulator absence is represented by the kernel version. Legacy mode assumes `platform_get_drvdata()` returns `skt_dev_info`. GPIO polarity and named descriptors must match board data.

Test signals: Platform probe for id-specific and legacy devices, GPIO acquisition, Vcc regulator enable/disable, reset and bus-enable toggling during socket state changes, card detect/ready GPIO events, and legacy H3600/Collie registration.

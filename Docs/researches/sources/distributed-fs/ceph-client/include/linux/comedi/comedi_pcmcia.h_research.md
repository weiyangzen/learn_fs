# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pcmcia.h

Purpose: This header provides Comedi helper APIs for PCMCIA-backed Comedi drivers.

Important APIs/types/functions: It declares `comedi_to_pcmcia_dev`, `comedi_pcmcia_enable`, `comedi_pcmcia_disable`, `comedi_pcmcia_auto_config`, `comedi_pcmcia_auto_unconfig`, `comedi_pcmcia_driver_register`, `comedi_pcmcia_driver_unregister`, and macro `module_comedi_pcmcia_driver`.

Control flow: A PCMCIA probe path auto-configures a Comedi device for the card. Enable calls may receive a `conf_check` callback for socket/resource validation. The module macro binds Comedi and PCMCIA driver registration lifetimes.

State and persistence behavior: State lives in PCMCIA socket/device resources and the attached Comedi device. Disable/unconfig releases configuration and Comedi attachment.

Dependencies and integration points: It includes PCMCIA CIS/driver headers and `comedidev.h`, integrating PCMCIA card services with Comedi core.

Risks: PCMCIA resource windows and configuration checks are hardware-sensitive. Failing to auto-unconfig on removal can leave stale Comedi devices. Probe ordering and card eject races need care.

Test signals: PCMCIA insertion/removal, configuration callback failure paths, module unload, Comedi minor cleanup, and I/O resource release validate behavior.

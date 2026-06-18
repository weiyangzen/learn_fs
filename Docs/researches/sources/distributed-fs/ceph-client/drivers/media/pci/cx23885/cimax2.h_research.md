# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.h

Declares the NetUP/CIMax2 CI interface used by cx23885 DVB and interrupt paths: CAM attribute/control accessors, slot reset/shutdown/TS control, IRQ status, poll status, init, and exit.

It includes DVB CA EN50221 definitions and relies on main-driver `cx23885_dev` and `cx23885_tsport` types. It is the boundary between transport-port setup and CAM hardware handling.

Risks are using IRQ/status paths before `netup_ci_init` sets `port_priv`, and missing CI teardown. Test signals are compile coverage, CI init/exit, and slot-status interrupt handling.

# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.c

Provides `cx18_video_set_io`, the narrow analog video routing helper for cx18. It reads `cx->active_input`, looks up the board's video input routing, and calls the AV decoder subdevice `video.s_routing`.

The file depends on `cx18-driver.h`, `cx18-video.h`, `cx18-cards.h`, valid card input tables, and an initialized `cx->sd_av`. It does not persist state itself; it applies current driver state to the subdevice.

Risks are invalid active input indexes, missing AV subdevice, and incorrect board routing table entries. Test signals are switching tuner/composite/S-video inputs and verifying decoder routing.

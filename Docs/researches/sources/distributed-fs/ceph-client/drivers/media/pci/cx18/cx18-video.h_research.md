# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.h

Declares `cx18_video_set_io(struct cx18 *cx)` for cx18 analog video input routing.

The interface integrates input-selection code with the AV decoder routing implementation. It assumes card input metadata and `sd_av` have already been initialized.

Risks are minimal but include duplicate inclusion without an include guard and misuse before AV setup. Test signals are compile coverage and analog input switching.

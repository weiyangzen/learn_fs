# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.c

## Purpose
This file implements the Atom ISP processing V4L2 subdevice, media pads, input format conversion tables, crop/compose behavior, controls, event subscription, video pipe initialization, and registration/cleanup.

## Important APIs and Functions
`atomisp_in_fmt_conv[]` maps mbus codes to AtomISP input formats and bayer order. Format helpers resolve compressed/uncompressed and AtomISP input formats. `atomisp_subdev_get_rect()` and `atomisp_subdev_get_ffmt()` retrieve active/try state. `atomisp_subdev_set_selection()` implements sink crop/source compose and updates CSS effective resolution/DVS envelope. `atomisp_subdev_set_ffmt()` applies formats and CSS input config. `atomisp_link_setup()` selects inputs from media links. `atomisp_init_subdev_pipe()` initializes vb2/video pipe state. `isp_subdev_init_entities()` creates the subdev, video node, and controls.

## Control Flow
`atomisp_subdev_init()` attaches the parent device, initializes stats/metadata lists, creates the media entity and capture video pipe, initializes the video device, and registers controls. Pad `set_fmt` validates sink codes, updates selection, and writes CSS resolution, binning, bayer order, input format, and ISYS defaults. Selection changes round dimensions, account for padding/DVS slack, update crop/compose, and set CSS effective resolution. Link setup powers down sensors on disable and selects the input matching the enabled CSI receiver.

## State and Persistence
Persistent state includes active pad formats/rectangles, control handler and controls, video pipe/vb2 queue, stats/metadata list heads, DIS lock, raw buffer bitmap lock, current parameters, and media pads. Try-state formats/rectangles live in V4L2 state. Event subscriptions live on the subdev devnode file-handle list.

## Dependencies and Integration Points
Depends on V4L2 subdev/media/vb2 APIs, AtomISP command helpers, CSS compatibility, file/ioctl operation tables, internals, and video-node helpers. It links CSI2 receiver source pads to the ISP sink and ISP source to the capture video node.

## Risks
Selection math mixes DVS, padding, aspect ratio, VFPP, and run modes. Source-pad format handling is limited. Frame-sync event subscription depends on CSS SOF validity. Pending-event cleanup assumes devnode/fh list availability. Many controls are added after a small initial handler allocation, so error checks matter.

## Test Signals
Use media-ctl for link enable/disable and input selection, test active/try formats, crop/compose under preview/video/still with DVS on/off, raw-to-YUV conversion, compressed raw helpers, event subscriptions, vb2 queue initialization, and unregister cleanup with pending events.

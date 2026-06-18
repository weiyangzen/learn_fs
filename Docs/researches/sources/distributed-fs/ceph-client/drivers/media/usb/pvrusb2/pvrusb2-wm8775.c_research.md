## sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-wm8775.c

### Purpose
`pvrusb2-wm8775.c` adapts pvrusb2 input selection to the wm8775 audio ADC V4L2 subdevice. It chooses the audio input route used for radio versus other inputs.

### Important APIs, Types, And Functions
The single exported implementation function is `pvr2_wm8775_subdev_update(struct pvr2_hdw *, struct v4l2_subdev *)`.

### Control Flow
When `input_dirty` or `force_dirty` is set, the function maps `PVR2_CVAL_INPUT_RADIO` to route `1` and all other inputs to route `2`, traces the selection, and invokes `sd->ops->audio->s_routing(sd, input, 0, 0)`.

### State, Persistence, And Dependencies
No state is owned by this file. It reads pvrusb2 hardware state and depends on V4L2 subdevice audio operations plus pvrusb2 tracing.

### Integration Points
It is used by the pvrusb2 hardware update path to keep the external audio digitizer synchronized with the currently selected logical input.

### Risks
The route mapping is intentionally simple and board-specific; unsupported hardware wiring would need a descriptor-driven scheme similar to the saa7115 adapter. The function assumes the wm8775 subdevice exposes `audio->s_routing`.

### Test Signals
Switching into and out of radio input should produce different wm8775 routes. Tests should confirm non-radio analog inputs all use the expected external audio route and that dirty flags gate redundant updates.

# sources/distributed-fs/openafs/src/gtx/lightobject.c

Purpose: implements GTX light objects, which display a label with highlight reflecting on/off state.

Important functions: exported `gator_light_ops`; `gator_light_create` allocates `struct gator_lightobj` and a `gwin_strparams` lower-level rock, initializes label, appearance and flash metadata, and attaches private data; `gator_light_display` draws the label through `WOP_DRAWSTRING`; `gator_light_set` updates logical setting and string highlight. Destroy and release are no-ops.

Control flow and state: creation assumes base `onode` fields are already filled by `objects.c`. Display casts `onp->o_data` to light data and `llrock` to string parameters. Setting does not redisplay automatically; callers must display later.

Dependencies and integration: uses `gtxlightobj.h`, `gtxwindows` draw macros via included object definitions, and global `objects_debug`.

Risks: allocated private data and string params are never freed by destroy/release; `strcpy` into fixed label buffer assumes bounded input; flash and outline flags are stored but not implemented. Test signals should include set/display highlight transitions, oversized labels, object destruction leaks, and unsupported appearance flags.

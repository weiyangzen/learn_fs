# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.c

Purpose: implements the VSP1 blend/ROP entities, covering both BRU and BRS variants. It exposes V4L2 subdev pad operations, a background-color control, and stream-time register programming for composition and alpha blending.

Important APIs and functions: `vsp1_brx_create()`, `brx_set_format()`, `brx_get_selection()`, `brx_set_selection()`, `brx_configure_stream()`, and the `brx_entity_ops` callback table. The file uses `struct vsp1_brx` from `vsp1_brx.h` and shared entity helpers.

Control flow: entity creation chooses BRU or BRS base registers and pad count, initializes the common entity, and installs `V4L2_CID_BG_COLOR`. Format setting forces all pads to ARGB8888 or AYUV, clamps dimensions, propagates sink-0 code to all pads, and resets compose rectangles. Selection controls per-input compose location with no scaling. During stream configuration, it writes input normalization, virtual background size/color, BRU ROP routing, per-input control, and blending coefficients to the display list body.

State and persistence: persistent state includes `bgcolor` and `inputs[i].rpf`, the latter set by DRM pipeline setup to mark active inputs. Pad formats and compose rectangles live in entity subdev state. Hardware state is persisted through display-list entries and refreshed whenever the pipeline is configured.

Dependencies and integration: depends on `vsp1_entity`, `vsp1_dl`, `vsp1_pipe`, `vsp1_rwpf`, and V4L2 controls. DRM code allocates and arbitrates BRU/BRS use; media-controller mode exposes links to userspace.

Risks and test signals: risks include mismatched pad format propagation, incorrect premultiplied-alpha handling, BRU/BRS input ordering, and background alpha assumptions. Test multi-plane DRM composition with z-order changes, UAPI media link setup through BRU/BRS, BG color control changes, and ARGB/AYUV format negotiation.

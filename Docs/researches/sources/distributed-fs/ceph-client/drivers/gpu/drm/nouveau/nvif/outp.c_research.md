# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/outp.c

## Purpose
This file wraps NVIF display output objects and exposes methods for DisplayPort, HDMI, LVDS, backlight, output-resource acquisition, inherited state, load detection, EDID, and detection.

## Important APIs, Types, and Functions
Key APIs include `nvif_outp_ctor/dtor`, DP MST/SST/drive/train/rates/AUX/power helpers, HDMI/infoframe/HDA ELD helpers, LVDS/backlight helpers, acquire/release helpers, inherit helpers, `nvif_outp_load_detect`, `nvif_outp_edid_get`, and `nvif_outp_detect`.

## Control Flow
Constructor creates an output object, translates backend type/protocol data into NVIF info fields, records heads/DDC/connector, and initializes OR state. Most helpers build a versioned method struct, call `nvif_mthd` or `nvif_object_mthd`, log errors, and return backend status or data. Acquire/inherit update `outp->or` from backend responses; release clears it.

## State and Persistence Behavior
Persistent state includes output ID, type/protocol capabilities, DP link info, head/DDC/connector masks, and current OR ID/link. EDID allocation returns a caller-owned buffer.

## Dependencies and Integration Points
It depends on NVIF display output ABI, DRM DP constants, display/KMS code, AUX/I2C/EDID code, and audio/infoframe paths.

## Risks
Many helpers trust caller-provided buffer sizes and protocol compatibility. AUX transfer copies back only the original requested size even if backend changes `args.size`. Constructor destroys the object on unknown type/protocol. OR state must be released on modeset failures.

## Test Signals
Signals include DP link training/MST VCPI, AUX transactions, EDID reads, HDMI infoframes/audio ELD, backlight get/set, output acquire/release, load detect, and protocol inheritance during takeover.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/tests/vkms_config_test.c

## Purpose

`vkms_config_test.c` is the KUnit suite for the VKMS topology configuration model. It tests creation/destruction, default-device construction, validation rules, link attachment/detachment, object iteration, cross-config rejection, and connector status storage.

## Important APIs and cases

The suite exercises `vkms_config_create()`, `vkms_config_default_create()`, destroy helpers, list iteration macros, getters/setters, `vkms_config_is_valid()`, and xarray-backed link helpers for planes-to-CRTCs, encoders-to-CRTCs, and connectors-to-encoders. The parameterized default-config test covers all combinations of cursor, writeback, overlay, and plane pipeline flags.

Validation tests cover zero and excessive counts, missing primary planes, duplicate primary/cursor planes for one CRTC, missing possible CRTCs/encoders, invalid connector linkage, and attaching objects from different `vkms_config` owners. Link tests verify duplicate attach errors and correct iteration after detach and destroy.

## Control flow and state

Each test creates isolated heap-backed `struct vkms_config` objects, mutates their lists/xarrays, asserts validity or pointer identity, and destroys them before return. There is no DRM device registration in this suite; it targets the configuration data model before instantiation.

## Dependencies and integration

It depends on `vkms_config.h` and KUnit-exported config functions. It protects configfs and default module-parameter paths because both feed the same topology creation and validation helpers before `vkms_create()`.

## Risks and test signals

Coverage is strong for in-memory topology invariants, ownership boundaries, and default configuration variants. It does not cover configfs lifetime/reference interactions or live device enable/disable. Passing `vkms-config` signals that the config layer rejects invalid topologies and maintains list/xarray consistency.

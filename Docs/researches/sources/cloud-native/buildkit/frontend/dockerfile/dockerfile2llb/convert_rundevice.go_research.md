# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_rundevice.go

Purpose: labs build-tag implementation for Dockerfile RUN CDI device mounts.

Important API: `dispatchRunDevices(c)` converts parsed device specs into `llb.AddCDIDevice` run options.

Control flow: selected by `//go:build dfrundevice`. For each device, it sets `llb.CDIDeviceName` and appends `llb.CDIDeviceOptional` when not required.

State and persistence: no persistent state; options affect the LLB exec op.

Dependencies and integration: called from `dispatchRun` and depends on instruction parser support plus LLB CDI support.

Risks and test signals: risks include feature-gate drift and optional/required inversion. Device integration tests under labs builds are the primary signal.

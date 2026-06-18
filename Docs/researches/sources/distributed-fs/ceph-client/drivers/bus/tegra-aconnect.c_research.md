# sources/distributed-fs/ceph-client/drivers/bus/tegra-aconnect.c

## Purpose
This NVIDIA Tegra210 ACONNECT bus driver enables runtime PM clock control for the audio/APE connection bus and populates its child devices.

## Important APIs, Types, and Functions
`struct tegra_aconnect` stores `ape` and `apb2ape` clocks. `tegra_aconnect_probe()` validates OF, gets clocks, enables runtime PM, populates children, and logs registration. Runtime PM callbacks prepare/enable both clocks on resume and disable/unprepare them on suspend. System sleep delegates to runtime PM force suspend/resume.

## Control Flow
Probe only binds to OF-backed devices, allocates state, gets the two clocks, stores drvdata, enables PM, and immediately populates children. Child device access is expected to cause runtime PM resumes when needed.

## State and Persistence
State is limited to the two clock handles. Clock enable state persists only while runtime PM considers the bus active.

## Dependencies and Integration Points
It depends on CCF clocks, OF platform population, runtime PM, and Tegra audio bus DT nodes. It integrates with ACONNECT child devices that require `ape` and `apb2ape` clocks.

## Risks and Test Signals
Risks include ignoring `of_platform_populate()` failures, no explicit child depopulation on remove, and children depending on runtime PM links being correct. Test signals include clock toggling on runtime PM transitions, child audio device probing, and clean system suspend/resume.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h

## Purpose
Defines the CAMSS core data structures, resource descriptors, supported SoC versions, and cross-module helper APIs used by the Qualcomm camera subsystem driver.

## Important APIs, Types, And Functions
- Defines `struct camss_subdev_resources`, `struct resources_icc`, `struct resources_wrapper`, `enum pm_domain`, `enum camss_version`, `struct camss_resources`, `struct camss`, `struct camss_camera_interface`, `struct camss_async_subdev`, `struct camss_clock`, and `struct parent_dev_ops`.
- Declares helpers for clocks, sensor discovery, link frequency/pixel clock, PM domains, VFE parent access, deletion, buffer done, and register update.
- Provides container macros for resolving parent `struct camss` or `struct device` from module arrays.

## Control Flow
No implementation is present, but this header defines the contracts used throughout probe, async binding, stream setup, and hardware interrupt handling. `camss.c` fills `struct camss_resources`, block init functions consume `struct camss_subdev_resources`, and CSID/VFE modules call back through parent helpers.

## State And Persistence
`struct camss` is the top-level in-memory state for a bound platform device. Resource structures are static descriptors. Async subdev structures retain parsed CSI lane configuration for external sensors while the notifier is active. No persistent storage is represented.

## Dependencies And Integration Points
Includes Linux device/types and V4L2/media headers plus CAMSS block headers. It is the primary integration header for CSIPHY, CSID, ISPIF, VFE, format handling, and core platform code.

## Risks And Edge Cases
Array sizes are capped by `CAMSS_RES_MAX`; resource tables must remain within those limits and null-terminate variable arrays. Container macros rely on module arrays and indices matching resource order. Adding a SoC version requires synchronized updates across resource tables, format/ops support, and version-specific conditionals.

## Test Signals
Build coverage across all CAMSS source files validates type contracts. Runtime test signals are successful probe, async sensor binding, media graph construction, VFE parent get/put behavior, clock programming, and buffer/register update routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h -->

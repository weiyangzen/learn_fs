# sources/distributed-fs/ceph-client/include/linux/regulator/mt6332-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6332 PMIC.

## Important APIs, Types, and Functions

The enum defines buck rails `VDRAM`, `VDVFS2`, `VPA`, `VRF1`, `VRF2`, `VSBST`, and LDO rails `VAUXB32`, `VBIF28`, `VDIG18`, `VSRAM_DVFS2`, `VUSB33`, ending with `MT6332_ID_VREG_MAX`.

## Control Flow

Driver descriptor arrays use these IDs for regulator registration and consumer mapping.

## State and Persistence Behavior

No state is defined in the header. PMIC register and regulator core state implement runtime behavior.

## Dependencies and Integration Points

It is standalone and integrates with MT6332 regulator driver code.

## Risks

ID ordering changes break descriptor indexing and bindings. Boost/RF/memory rails have different capabilities and must be mapped correctly.

## Test Signals

Tests should cover descriptor coverage, DT supply matching, and per-rail voltage/enable capabilities.

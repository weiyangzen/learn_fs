# sources/distributed-fs/ceph-client/net/can/Kconfig

## Purpose
Defines the kernel configuration menu for the Controller Area Network protocol family and core CAN socket protocols.

## Important APIs, Types, And Functions
The file declares `CAN`, `CAN_RAW`, `CAN_BCM`, `CAN_GW`, sources `net/can/j1939/Kconfig`, and declares `CAN_ISOTP`. `CAN` selects `SKB_EXTENSIONS`.

## Control Flow
When `CAN` is enabled, users can select raw CAN sockets, Broadcast Manager sockets, CAN gateway/router support, J1939 options from the sourced Kconfig, and ISO-TP segmented transport support. Several protocol options default to `y` when CAN is enabled.

## State And Persistence Behavior
No runtime state exists. Selected symbols persist in kernel configuration and drive built-in/module/absent protocol availability.

## Dependencies And Integration Points
Integrates with `net/can/Makefile`, PF_CAN core code, socket protocols, J1939 subdirectory configuration, and networking documentation referenced by help text.

## Risks And Test Signals
Risks include default-enabling protocols unexpectedly, missing dependencies for protocol modules, or breaking sourced J1939 config visibility. Signals include Kconfig linting, `oldconfig`, `allmodconfig`, protocol module builds, and runtime socket creation tests for CAN_RAW, CAN_BCM, CAN_GW, J1939, and CAN_ISOTP.

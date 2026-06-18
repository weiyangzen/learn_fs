# sources/distributed-fs/ceph-client/drivers/power/reset/th1520-aon-reboot.c

## Purpose
T-Head TH1520 AON firmware poweroff/restart auxiliary driver.

## Important APIs, Types, and Functions
packed empty RPC message, poweroff/restart sys-off callbacks, and auxiliary-device probe.

## Control Flow
probe receives `struct th1520_aon_chan` via platform data from PM-domain/AON parent and registers poweroff and restart handlers; callbacks send WDG service RPC functions for power off or restart.

## State and Persistence Behavior
no owned persistent hardware state; AON firmware channel and parent own communication state.

## Dependencies and Integration Points
auxiliary bus, TH1520 AON firmware RPC API, sys-off handlers.

## Risks and Edge Cases
platform_data must be a valid channel; RPC return value is ignored; firmware protocol size constants must match.

## Test Signals
auxiliary match, missing/invalid channel, RPC tracing, poweroff/restart firmware tests.

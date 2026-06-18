# sources/distributed-fs/ceph-client/drivers/s390/cio/css.h

## Purpose
This header defines the CSS bus contract: path-grouping constants, PGID/path-state data, CSS driver callbacks, channel-subsystem state, slow-path scheduling APIs, and subchannel registration helpers.

## Important APIs, Types, and Functions
It defines path grouping constants (`SPID_*`, `SNID_*`), `enum css_eval_cond`, `struct path_state`, `struct extended_cssid`, `struct pgid`, `struct css_driver`, and `struct channel_subsystem`. Public declarations include CSS driver registration, subchannel allocation/registration/unregistration/lookup, staged and brute-force subchannel iteration, SSD refresh, slow-path scheduling/completion, pseudo-subchannel checks, `css_sch_is_valid()`, and the global `cio_work_q`.

## Control Flow
There is no standalone flow. CSS drivers provide `irq`, `chp_event`, `sch_event`, `probe`, `remove`, `shutdown`, and `settle` callbacks, which `css.c` invokes from interrupt and process contexts. Inline `css_by_id()` and `for_each_css()` currently map all lookups to the singleton CSS.

## State and Persistence
The header describes volatile CSS state: registered channel paths, global PGID, measurement buffers, pseudo-subchannel, and synchronization primitives. No persistence is defined.

## Dependencies and Integration Points
It depends on Linux device/workqueue/wait/mutex types and architecture CIO/CHPID/SCHID headers. It is included by channel-path, CHSC, CIO, device, and CMF code.

## Risks and Test Signals
Risk areas include singleton CSS helpers, callback context expectations, structure lifetime across bus unregister, and path-grouping bitfield layout. Test signals include compiling all CSS drivers, boot discovery, multi-subchannel-set enablement, slow-path scheduling, and future work involving multiple CSS instances.

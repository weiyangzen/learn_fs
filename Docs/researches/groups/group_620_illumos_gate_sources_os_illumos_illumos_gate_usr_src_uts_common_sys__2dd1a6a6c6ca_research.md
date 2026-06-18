# Group Research: group_620_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__2dd1a6a6c6ca

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconf.h

## Purpose
Defines the shared kernel/sysconf utility representation of `/etc/system` entries and module-control command constants.

## Main Interfaces
- `struct sysparam`: linked-list record for parsed `/etc/system` entries, including command type, operation, module name, token/config strings, numeric info, allocated address list, and duplicate/termination flags.
- `struct modcmd`: command-name to command-type mapping.
- Module command constants:
  - `MOD_EXCLUDE`, `MOD_INCLUDE`, `MOD_FORCELOAD`
  - root/swap device and filesystem directives
  - `MOD_MODDIR`, `MOD_SET`, `MOD_SET32`, `MOD_SET64`
- `mod_sysctl()` command constants:
  - `SYS_FORCELOAD`, `SYS_SET_KVAR`, `SYS_SET_MVAR`, `SYS_CHECK_EXCLUDE`
- Assignment operation constants: `SETOP_ASSIGN`, `SETOP_AND`, `SETOP_OR`.

## Dependencies And Relationships
This header is consumed by boot/module configuration code that parses `/etc/system` and later applies kernel/module variable settings or load policy.

## Research Notes
The file is a compact ABI for system configuration parsing. The `SYSPARAM_*` flags distinguish token types, duplicate entries, and terminal list entries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconfig.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconfig.h

## Purpose
Defines command numbers for the undocumented `_sysconfig` system call and declares the machine-specific kernel helper.

## Main Interfaces
- Kernel-only `mach_sysconfig(int)`.
- `_CONFIG_*` command constants for configured limits and machine characteristics:
  - process, group, open-file, page-size, clock tick, POSIX/X/Open version values
  - processor counts, async I/O, message queues, realtime signals, semaphores, timers
  - physical/available pages and cache/coherency data
  - max PID, stack protection, CPU ID, symlink loop max, ephemeral ID max, user address max, and `NCPU`.

## Dependencies And Relationships
Used by the `_sysconfig` syscall implementation and architecture-specific code that supplies machine-dependent values.

## Research Notes
The file explicitly warns that `_sysconfig` is undocumented and not a stable future-compatibility interface. Command values are numeric ABI and must be treated as fixed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc.h

## Purpose
Provides the public kernel entry point for the system duty-cycle scheduling class support.

## Main Interfaces
- `SYSDC_THREAD_BATCH`: marks a thread as doing batch processing.
- `sysdc_thread_enter(struct _kthread *, uint_t, uint_t)`: moves/configures a thread for SDC behavior.

## Dependencies And Relationships
Includes `sys/types.h` and forward-declares `struct _kthread`. The implementation details live in `sysdc_impl.h`.

## Research Notes
This is the narrow public boundary; most SDC state and accounting is deliberately hidden in the implementation header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc_impl.h

## Purpose
Defines private implementation state for SDC, including per-processor-set duty-cycle accounting, per-thread class data, active-thread hash buckets, and class-entry parameters.

## Main Interfaces
- `sysdc_pset_t`: tracks SDC state for a CPU partition, including thread references, on-processor time, break decisions, and debugging counters.
- `sysdc_t`: per-thread SDC data stored via `t_cldata`, including target duty cycle, priority range, associated processor set, timing bases, sleep/update counters, computed priorities, and debug fields.
- `sysdc_list_t`: hash bucket for active SDC threads with a lock and cache-line padding.
- `sysdc_params_t`: arguments passed to `CL_ENTERCLASS()`.
- `SYSDC_DC_MAX`: maximum valid duty-cycle percentage.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/list.h`, and `sys/sysdc.h`. It references `struct _kthread` and `struct cpupart`, tying it to the scheduler, CPU partitioning, and per-thread scheduling-class data.

## Research Notes
Locking comments are part of the contract: fields are protected by `sdl_lock`, `thread_lock()`, or coordination between the thread and `sysdc_update()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent.h

## Purpose
Defines the public sysevent API, common event data types, limits, event-channel flags, and separate userland/kernel interfaces for publishing, subscribing, and inspecting events.

## Main Interfaces
- Opaque handles:
  - `sysevent_t`
  - `evchan_t`
- Attribute and identifier types:
  - `sysevent_attr_list_t`
  - `sysevent_attr_t`
  - `sysevent_id_t`
  - `sysevent_value_t`
  - `sysevent_bytes_t`
- Common constants:
  - event allocation flags `SE_SLEEP`, `SE_NOSLEEP`
  - sysevent error codes `SE_EINVAL` through `SE_NO_TRANSPORT`
  - publisher prefixes such as `SUNW:kern:`, `SUNW:usr:`, and `ILLUMOS:kern:`
  - class, subclass, publisher, channel, subscriber, and payload size limits
- Shared event channel APIs:
  - `sysevent_evc_bind()`, `sysevent_evc_unbind()`
  - `sysevent_evc_subscribe()`, `sysevent_evc_unsubscribe()`
  - `sysevent_evc_publish()`
  - `sysevent_evc_control()`
  - property nvlist get/set helpers
- Userland-only subscription attribute APIs and extended subscribe support.
- Kernel-only log/event construction APIs such as `log_sysevent()`, `sysevent_alloc()`, `sysevent_add_attr()`, and event getter functions.

## Dependencies And Relationships
Uses `sys/nvpair.h` and `sys/null.h`; userland path also uses `door.h`. Internal wire/storage layout and driver ioctls are defined in `sysevent_impl.h`.

## Research Notes
The publish flags distinguish allocation behavior from queue-wait behavior. `EVCH_TRYHARD` is kernel-only, while persistent subscriptions are controlled by `EVCH_SUB_KEEP`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/datalink.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/datalink.h

## Purpose
Defines payload attribute names for datalink sysevents, specifically link-state events.

## Main Interfaces
- `DATALINK_EV_LINK_NAME`: datalink name attribute.
- `DATALINK_EV_LINK_ID`: `datalink_id_t` attribute.
- `DATALINK_EV_ZONE_ID`: zone ID attribute.

## Dependencies And Relationships
The comments define the schema for `EC_DATALINK` / `EC_DATALINK_LINK_STATE` events. Actual class/subclass strings are supplied by sysevent event definition headers.

## Research Notes
This is a schema-name header only; it deliberately contains no functions or structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/datalink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dev.h

## Purpose
Defines public device sysevent payload schemas and attribute names for device add/remove and device-branch events.

## Main Interfaces
- Attribute names:
  - `EV_VERSION`
  - `DEV_PHYS_PATH`
  - `DEV_NAME`
  - `DEV_DRIVER_NAME`
  - `DEV_INSTANCE`
  - `DEV_PROP_PREFIX`
- Version constant `EV_V1`.
- Property limits:
  - `MAX_PROP_COUNT`
  - `PROP_LEN_LIMIT`

## Dependencies And Relationships
Includes `sys/sysevent/eventdefs.h` for device class/subclass names such as device add/remove and branch add/remove. Used by device tree and devfs event producers.

## Research Notes
The schema comments cover disk, network, printer, and device-branch events. Add events may include selected devinfo node properties via the `prop-` prefix; remove events use the core identifying fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/domain.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/domain.h

## Purpose
Defines payload attribute names and values for domain state-change sysevents.

## Main Interfaces
- `DOMAIN_VERSION`
- `DOMAIN_WHAT_CHANGED`
- `DOMAIN_KEYSWITCH`
- `DOMAIN_FRU`
- `DOMAIN_RESERVED_ATTR`

## Dependencies And Relationships
Schema comments target `EC_DOMAIN` / `ESC_DOMAIN_STATE_CHANGE` events published by domain environment monitoring code.

## Research Notes
The header is a small event-schema vocabulary for consumers that interpret domain FRU or keyswitch state changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/domain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dr.h

## Purpose
Defines dynamic reconfiguration sysevent attribute names, values, and helper conversions for attachment-point, request, and target-state events.

## Main Interfaces
- Attachment point attributes and values:
  - `DR_AP_ID`
  - `DR_HINT`
  - `DR_HINT_INSERT`
  - `DR_HINT_REMOVE`
  - `DR_RESERVED_ATTR`
- Hint constants and converter:
  - `SE_NO_HINT`
  - `SE_HINT_INSERT`
  - `SE_HINT_REMOVE`
  - `SE_HINT2STR(h)`
- Request attributes and values:
  - `DR_REQ_TYPE`
  - `DR_REQ_INCOMING_RES`
  - `DR_REQ_OUTGOING_RES`
  - `DR_REQ_INVESTIGATE_RES`
  - `SE_REQ2STR(h)`
- Target attribute:
  - `DR_TARGET_ID`

## Dependencies And Relationships
Schema comments cover `EC_DR` subclasses for attachment-point state changes, DR requests, and target state changes. Producers include DR subsystems and drivers.

## Research Notes
The header states that public DR sysevent schema changes require PSARC approval, so these string values are compatibility-sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/dr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/env.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/env.h

## Purpose
Defines environmental-monitor sysevent payload attributes and state constants for temperature, power, fan, and LED events.

## Main Interfaces
- Common attributes:
  - `ENV_VERSION`
  - `ENV_FRU_ID`
  - `ENV_FRU_RESOURCE_ID`
  - `ENV_FRU_DEVICE`
  - `ENV_FRU_STATE`
  - `ENV_MSG`
  - `ENV_RESERVED_ATTR`
- FRU state constants:
  - `ENV_OK`
  - `ENV_WARNING`
  - `ENV_FAILED`
- LED state constants:
  - `ENV_LED_ON`
  - `ENV_LED_OFF`
  - `ENV_LED_BLINKING`
  - `ENV_LED_FLASHING`
  - `ENV_LED_INACCESSIBLE`
  - `ENV_LED_STANDBY`
  - `ENV_LED_NOT_PRESENT`

## Dependencies And Relationships
Schema comments target `EC_ENV` subclasses such as temp, power, fan, and LED. Producers are environmental monitor components.

## Research Notes
The file is schema-oriented. It standardizes attribute names and enumerated payload values but does not define the event class strings themselves.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/env.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/eventdefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/eventdefs.h

## Purpose
Central registry of public sysevent class and subclass string constants.

## Main Interfaces
- Generic/internal classes: `EC_NONE`, `EC_PRIV`.
- Hardware/platform classes including DR, domain, environment, IPMP, device, fault management, platform, power control, ACPI, ZFS, datalink, VRRP, and PCIe.
- Subclass constants for:
  - DR attachment point, request, and target-state changes.
  - Domain state/loghost changes.
  - IPMP group, interface, member, and probe changes.
  - Device add/remove/branch/DLE/eject events.
  - FMA errors and replays.
  - Power control and ACPI events.
  - ZFS pool, vdev, scrub, resilver, trim, config, and history events.
  - Datalink link state, VRRP state change, and PCIe link state.

## Dependencies And Relationships
Included by schema-specific headers such as `sysevent/dev.h` and by event producers/consumers that need the canonical class/subclass strings.

## Research Notes
This file is a compatibility boundary. The string values are the event taxonomy visible to userland listeners and administrative tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/eventdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/ipmp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/ipmp.h

## Purpose
Defines Sun-private IPMP sysevent channel, payload attribute names, versions, and enumerations for group, interface, member, and probe events.

## Main Interfaces
- Event channel: `IPMP_EVENT_CHAN`.
- Common/event version attributes:
  - `IPMP_EVENT_VERSION`
  - `IPMP_EVENT_CUR_VERSION`
- Group state/change attributes:
  - `IPMP_GROUP_NAME`
  - `IPMP_GROUP_SIGNATURE`
  - `IPMP_GROUP_STATE`
  - `IPMP_GROUPLIST_SIGNATURE`
  - `IPMP_GROUP_OPERATION`
- Enums for group state and group operation.
- Interface/member attributes:
  - `IPMP_IF_OPERATION`
  - `IPMP_IF_NAME`
  - `IPMP_IF_TYPE`
  - `IPMP_IF_STATE`
- Enums for interface operation, type, and state.
- Probe attributes:
  - `IPMP_PROBE_ID`
  - `IPMP_PROBE_STATE`
  - probe timing fields
  - `IPMP_PROBE_TARGET`
  - RTT average/deviation attributes
- Probe state enum.

## Dependencies And Relationships
Schema comments map these payloads to `EC_IPMP` subclasses in `eventdefs.h`. The publisher is `in.mpathd`.

## Research Notes
The header states these definitions are private and subject to change. The schema is still important for IPMP event consumers that bind to the named channel.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/ipmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pcie.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pcie.h

## Purpose
Defines payload attribute names and detector flags for PCIe link-state sysevents.

## Main Interfaces
- `PCIE_EV_DETECTOR_PATH`: devfs path of detector node.
- `PCIE_EV_CHILD_PATH`: devfs path of updated child node.
- `PCIE_EV_DETECTOR_FLAGS`: PCIe change flags.
- Detector flags:
  - `PCIE_EV_DETECTOR_FLAGS_LBMS`
  - `PCIE_EV_DETECTOR_FLAGS_LABS`

## Dependencies And Relationships
Schema comments target `ESC_PCIE_LINK_STATE` events under `EC_PCIE`.

## Research Notes
This is a small schema header used to make PCIe link-change payloads self-describing and stable across producers/consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pcie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pwrctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pwrctl.h

## Purpose
Defines power-control sysevent schema details for ACPI/power-related add, remove, warning, low, state-change, button, and brightness events.

## Main Interfaces
- The file documents common attributes for `EC_PWRCTL` events, including version, ACPI hardware ID, UID, device index, and event-specific fields.
- `PWRCTL_BRIGHTNESS_LEVEL`: brightness-level payload attribute for brightness events.

## Dependencies And Relationships
Pairs with `EC_PWRCTL` and `ESC_PWRCTL_*` constants in `eventdefs.h`. Producers are power-control and ACPI/environmental monitor paths.

## Research Notes
Most of the contract is carried in comments describing the schema. The only macro in the file is the brightness-level attribute name.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pwrctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/vrrp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/vrrp.h

## Purpose
Defines VRRP sysevent publisher and payload attribute names for router state-change events.

## Main Interfaces
- `VRRP_EVENT_PUBLISHER`: publisher name, `vrrpd`.
- Attributes:
  - `VRRP_EVENT_VERSION`
  - `VRRP_EVENT_ROUTER_NAME`
  - `VRRP_EVENT_STATE`
  - `VRRP_EVENT_PREV_STATE`
- `VRRP_EVENT_CUR_VERSION`.

## Dependencies And Relationships
Schema comments target VRRP events, especially `ESC_VRRP_STATE_CHANGE` under the VRRP sysevent class.

## Research Notes
This header defines the payload vocabulary only; state value meanings come from the VRRP daemon/domain logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/vrrp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent_impl.h

## Purpose
Defines the private sysevent implementation ABI: packed event buffer layout, attribute packing helpers, syseventd door upcall structures, channel/subscriber internals, kernel private entry points, event-channel ioctl payloads, and `/dev/sysevent` constants.

## Main Interfaces
- Packed event representation:
  - `se_name_t`
  - `se_value_t`
  - `sysevent_attr_impl_t`
  - `sysevent_hdr_t`
  - `sysevent_impl_t`
- Event access and layout macros:
  - `SYSEVENT_IMPL()`, `SE_VERSION()`, `SE_CLASS_NAME()`, `SE_SUBCLASS_NAME()`, `SE_PUB_NAME()`
  - `SE_ALIGN()`, `SE_SIZE()`, `SE_ATTR_OFF()`
  - `SYS_EVENT_VERSION`, `SE_PACKED_BUF`
- Door/upcall queue structures:
  - `log_event_upcall_arg_t`
  - `log_eventq_t`
  - `LOGEVENT_DOOR_UPCALL`
- Registration/channel structures:
  - `subclass_lst_t`
  - `class_lst_t`
  - `se_pubsub_t`
  - `sysevent_channel_descriptor_t`
- Kernel-private log APIs: `log_event_init()`, `log_sysevent_flushq()`, `log_usr_sysevent()`, copyout/free/register helpers, and ID generation.
- Event channel internals:
  - queue/list primitives `evch_dlelem_t`, `evch_dlist_t`, `evch_qelem_t`, `evch_squeue_t`
  - callback typedefs
  - `evch_gevent_t`, `evch_eventq_t`, `evch_evqsub_t`, `evch_subd_t`, `evch_chan_t`, `evch_bind_t`, `evchanq_t`
- User-channel private APIs for open, close, allocate, post, subscribe, control, unsubscribe, channel data, properties, and walking queued events.
- Driver ioctl constants and packed argument structures:
  - `SEV_PUBLISH`, `SEV_CHAN_OPEN`, `SEV_CHAN_CONTROL`, `SEV_SUBSCRIBE`, `SEV_UNSUBSCRIBE`, `SEV_CHANNAMES`, `SEV_CHANDATA`, property ioctls
  - `sev_bind_args_t`, `sev_control_args_t`, `sev_publish_args_t`, `sev_subscribe_args_t`, `sev_unsubscribe_args_t`, `sev_chandata_args_t`, `sev_propnvl_args_t`

## Dependencies And Relationships
Includes `sys/nvpair.h`, `sys/id_space.h`, and `sys/door.h`. It backs the public API in `sysevent.h` and the `/dev/sysevent` driver/userland protocol.

## Research Notes
The comments warn not to alter packed structures without careful testing. Layout is intentionally 64-bit aligned, with pack pragmas for cross-ABI structure compatibility where needed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysinfo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysinfo.h

## Purpose
Defines kernel CPU, system, and VM accounting structures exported through kstats and historical system statistics interfaces.

## Main Interfaces
- State constants:
  - `CPU_IDLE`, `CPU_USER`, `CPU_KERNEL`, `CPU_WAIT`, `CPU_STATES`
  - wait-state constants `W_IO`, `W_SWAP`, `W_PIO`, `W_STATES`
- Legacy/stat structures:
  - `cpu_sysinfo_t`
  - `sysinfo_t`
  - `cpu_syswait_t`
  - `cpu_vminfo_t`
  - `vminfo_t`
  - `cpu_stat_t`
- 64-bit kstat-oriented structures:
  - `cpu_sys_stats_t`
  - `cpu_vm_stats_t`
  - `cpu_stats_t`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/t_lock.h`, `sys/kstat.h`, and `sys/machlock.h`. Filesystems and VM paths increment counters such as block reads/writes, name lookups, UFS inode stats, paging, COW faults, and filesystem page activity.

## Research Notes
This is an accounting ABI, not logic. Several fields are retained as unused/compatibility counters, and comments document how tools like `sar(1)` interpret logical vs physical read/write counters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syslog.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syslog.h

## Purpose
Defines syslog facility, priority, mask, and openlog option constants.

## Main Interfaces
- Facility constants:
  - `LOG_KERN`, `LOG_USER`, `LOG_MAIL`, `LOG_DAEMON`, `LOG_AUTH`, `LOG_SYSLOG`, `LOG_LPR`, `LOG_NEWS`, `LOG_UUCP`, cron/authpriv/FTP/NTP/audit/console/local facilities.
- Facility helpers:
  - `LOG_NFACILITIES`
  - `LOG_FACMASK`
- Priority constants:
  - `LOG_EMERG` through `LOG_DEBUG`
  - `LOG_PRIMASK`
- Mask helpers:
  - `LOG_MASK(pri)`
  - `LOG_UPTO(pri)`
- `openlog()` options:
  - `LOG_PID`, `LOG_CONS`, `LOG_ODELAY`, `LOG_NDELAY`, `LOG_NOWAIT`

## Dependencies And Relationships
Used by kernel and userland logging paths that need canonical syslog encoding values.

## Research Notes
This is a compatibility header with BSD/AT&T heritage. Numeric encodings are ABI and protocol relevant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syslog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmacros.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmacros.h

## Purpose
Provides common low-level macros for block/byte conversion, min/max/absolute values, device number encoding/decoding, power-of-two alignment, bitfield declaration ordering, atomic count helpers, array sizing, and saturating integer conversions.

## Main Interfaces
- Block conversion macros: `dtob()`, `btod()`, `btodt()`, `lbtod()`.
- Generic macros: `MIN`, `MAX`, `ABS`, `SIGNOF`, `__DECONST`.
- Kernel BCD conversion tables/macros:
  - `byte_to_bcd`, `bcd_to_byte`
  - `BYTE_TO_BCD()`, `BCD_TO_BYTE()`
- Device-number macros:
  - old and expanded major/minor bit constants
  - `major()`, `minor()`, `getmajor()`, `getminor()`
  - `makedev()`, `makedevice()`
  - `emajor()`, `eminor()`, `getemajor()`, `geteminor()`
  - `DEVCMPL()`, `DEVEXPL()`, `cmpdev()`, `expdev()`
- Alignment and rounding macros:
  - `IS_P2ALIGNED()`, `howmany()`, `roundup()`, `ISP2()`
  - `P2ALIGN()`, `P2PHASE()`, `P2NPHASE()`, `P2ROUNDUP()`, `P2END()`, `P2PHASEUP()`, `P2BOUNDARY()`, `P2SAMEHIGHBIT()`
  - typed variants for explicit result widths
- Count and bitfield helpers:
  - `INCR_COUNT()`, `DECR_COUNT()`
  - `DECL_BITFIELD2()` through `DECL_BITFIELD8()`
- `ARRAY_SIZE()`, `UINT64_OVERFLOW_ADD()`, and `UINT64_OVERFLOW_TO_INT64()`.

## Dependencies And Relationships
Includes `sys/param.h` and `sys/stddef.h`. It is widely included across kernel and userland headers and is especially important for device IDs and alignment-sensitive kernel code.

## Research Notes
The file warns that older major/minor macros should not be used by drivers or applications. Endianness-specific `DECL_BITFIELD*` macros require either `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmacros.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmsg_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmsg_impl.h

## Purpose
Defines private `/dev/sysmsg` path and ioctl command constants used by `consadm(8)` to manage auxiliary console devices.

## Main Interfaces
- Device path: `SYSMSG`.
- Ioctls:
  - `CIOCGETCONSOLE`: query auxiliary console device names.
  - `CIOCSETCONSOLE`: set an auxiliary console.
  - `CIOCRMCONSOLE`: remove an auxiliary console.
  - `CIOCTTYCONSOLE`: return the controlling tty `dev_t`.

## Dependencies And Relationships
Used by the sysmsg module and console administration tooling.

## Research Notes
The ioctl semantics are documented in comments, including the two-step size/query behavior for `CIOCGETCONSOLE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmsg_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systeminfo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systeminfo.h

## Purpose
Defines `sysinfo(2)` command constants, kernel backing string symbols, and host/domain/platform identifier limits.

## Main Interfaces
- Kernel symbols:
  - `architecture`
  - `architecture_32`
  - `hw_serial`
  - `hw_provider`
  - `srpc_domain`
  - `platform`
- UI-defined get commands:
  - `SI_SYSNAME`, `SI_HOSTNAME`, `SI_RELEASE`, `SI_VERSION`, `SI_MACHINE`, `SI_ARCHITECTURE`, `SI_HW_SERIAL`, `SI_HW_PROVIDER`, `SI_SRPC_DOMAIN`
- UI-defined set commands:
  - `SI_SET_HOSTNAME`, `SI_SET_SRPC_DOMAIN`
- illumos-defined get commands:
  - `SI_PLATFORM`, `SI_ISALIST`, `SI_DHCP_CACHE`, `SI_ARCHITECTURE_32`, `SI_ARCHITECTURE_64`, `SI_ARCHITECTURE_K`, `SI_ARCHITECTURE_NATIVE`, `SI_ADDRESS_WIDTH`
- Limits:
  - `HW_INVALID_HOSTID`
  - `HW_HOSTID_LEN`
  - `DOM_NM_LN`
- Userland declaration: `sysinfo(int, char *, long)`.

## Dependencies And Relationships
The command values are consumed by the `sysinfo(2)` syscall implementation and userland callers. The kernel symbols are filled by platform/boot code.

## Research Notes
The header documents the numeric allocation scheme for UI and illumos get/set commands. Existing command values are fixed due to historical registration/compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systeminfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systm.h

## Purpose
Defines broad kernel system interfaces: global kernel state variables, boot/startup hooks, time-of-day status, timeout/callout APIs, copyin/copyout and low-level memory/string helpers, fault handling, SPL/softcall interfaces, syscall table structures, syscall return values, and kernel/boot string/memory prototypes.

## Main Interfaces
- Kernel globals for clock rate, root/devices vnodes, memory counters, root device/vnode, panic state, scheduler wake flags, kernel text/data bounds, auditing, load averages, ISA list, stack execution policy, NFS zone policy, `maxusers`, and `pidmax`.
- Startup/platform hooks:
  - `startup()`, `clkstart()`, `post_startup()`, `kern_setup1()`, `ka_init()`, `nodename_set()`
- TOD fault support:
  - `enum tod_fault_type`
  - `TOD_*` status flags
  - `tod_validate()`, `tod_status_set()`, `tod_status_clear()`, `plat_tod_fault()`
- Timers/callouts:
  - `timeout()`, `realtime_timeout()`, `untimeout()`
  - generic/default callout APIs and `delay*()` helpers
- Device and conversion helpers:
  - `getudev()`, `cmpldev()`, `expldev()`, `stoi()`, `numtos()`, suboption helpers
- User/kernel copying and fault helpers:
  - `copyin()`, `copyout()`, `copyinstr()`, `copyoutstr()`, `xcopy*()`, `fuword*()`, `suword*()`, no-error variants
  - `on_fault()`, `no_fault()`, `setjmp()`, `longjmp()`
- Memory/string primitives for kernel/boot:
  - `bcopy()`, `bzero()`, `memset()`, `memcpy()`, `memcmp()`, `strlcpy()`, `strlen()`, `strcmp()`, and related functions
- Interrupt/SPL and softcall:
  - `spl*()` functions, `splx()`, `softcall_init()`, `softcall()`, `softint()`
- System call dispatch:
  - `struct sysent`
  - `sysent[]`, `sysent32[]`, `nosys_ent`
  - `NSYSCALL`, syscall flag constants, `rval_t`
  - syscall argument and dispatch helpers
- Overflow helper inline functions for `uint16_t`, `hrtime_t`, and `off_t`.

## Dependencies And Relationships
Pulls different dependencies for standalone vs kernel builds. It is one of the central kernel headers and is used by syscall, VM, device, scheduler, boot, and low-level utility code.

## Research Notes
Several comments define compatibility requirements, especially for `struct sysent`: expansion should only occur at the end, flags must not be reused, and size is performance-sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systrace.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systrace.h

## Purpose
Defines the kernel interface between the syscall table and DTrace systrace provider.

## Main Interfaces
- `systrace_sysent_t`: per-syscall DTrace probe IDs and original syscall function pointer.
- Kernel globals:
  - `systrace_sysent`
  - `systrace_sysent32`
  - `systrace_probe`
- Functions:
  - `systrace_stub()`
  - `dtrace_systrace_syscall()`
  - `dtrace_systrace_syscall32()` under `_SYSCALL32_IMPL`

## Dependencies And Relationships
Includes `sys/dtrace.h`. Interposes on syscall entry/return while preserving the underlying syscall handler pointer.

## Research Notes
This is kernel-only. It provides the syscall instrumentation dispatch bridge rather than the DTrace provider implementation itself.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_kuser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_kuser.h

## Purpose
Defines kernel TLI/TPI helper structures and function prototypes used by in-kernel transport clients.

## Main Interfaces
- `TIUSER`: kernel transport endpoint wrapper containing file pointer, transport provider info, and flags.
- `struct knetbuf`: STREAMS-backed kernel netbuf for received data.
- `struct t_kunitdata`: unitdata address/options/data container.
- Debug macro `KTLILOG()` under `KTLIDEBUG`.
- Flag `MADE_FP`.
- Kernel TLI operations:
  - `t_kalloc()`, `t_kfree()`
  - `t_kopen()`, `t_kclose()`
  - `t_kbind()`, `t_kunbind()`
  - `t_kconnect()`
  - `t_koptmgmt()`
  - `t_krcvudata()`, `t_ksndudata()`
  - `t_kspoll()`, `t_kgetstate()`
  - `tli_send()`, `tli_recv()`
  - `t_tlitosyserr()`, `get_ok_ack()`
- Size helper macros for TPI primitives.

## Dependencies And Relationships
Includes file, credential, STREAMS, and TLI user headers. Used by kernel subsystems that need transport-provider access through TLI/TPI rather than socket APIs.

## Research Notes
The comments note that `TIUSER` would need expansion for richer connection-oriented transport state. Current data structures are minimal wrappers around provider info and STREAMS messages.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_kuser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_lock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_lock.h

## Purpose
Aggregates core kernel synchronization headers and declares dispatcher-lock routines/macros.

## Main Interfaces
- Includes, outside assembly:
  - `sys/machlock.h`
  - `sys/param.h`
  - `sys/mutex.h`
  - `sys/rwlock.h`
  - `sys/semaphore.h`
  - `sys/condvar.h`
- Kernel dispatcher lock routines:
  - `disp_lock_enter()`, `disp_lock_exit()`
  - high-priority and no-preempt variants
  - `disp_lock_init()`, `disp_lock_destroy()`
- Dispatcher lock macros:
  - `DISP_LOCK_INIT()`
  - `DISP_LOCK_HELD()`
  - `DISP_LOCK_DESTROY()`
- Static/runtime assertion placeholders:
  - `NO_LOCKS_HELD`
  - `NO_COMPETING_THREADS`

## Dependencies And Relationships
Used by scheduler and synchronization users. `disp_lock_t` is defined in `machlock.h`.

## Research Notes
The file is mostly an include/dispatcher-lock boundary. It preserves compatibility with assembly consumers via `_ASM` guards.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/task.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/task.h

## Purpose
Defines illumos task/project membership interfaces, task flags, kernel task accounting state, and userland task ID syscalls.

## Main Interfaces
- Task flags:
  - `TASK_NORMAL`
  - `TASK_FINAL`
  - `TASK_MASK`
  - project purge flags
- Kernel `task_t`: task ID, flags, project, hold count, member process list, usage accounting, resource controls, LWP/process limits, CPU time/ticks, zone, inherited usage, kstats, and commit-list linkage.
- `task_kstat_t`: zonename, usage, and value kstat fields.
- Kernel globals/resource-control handles:
  - `task0p`
  - `rc_task_lwps`
  - `rc_task_nprocs`
  - `rc_task_cpu_time`
- Kernel APIs:
  - task init/create/begin/attach/change/detach/join/hold/release/end
  - lookup by task ID and zone
  - CPU time increment
  - task commit thread init
- Userland APIs:
  - `settaskid()`
  - `gettaskid()`

## Dependencies And Relationships
Includes `sys/param.h`, `sys/types.h`, and `sys/rctl.h`; kernel path includes ID-space, extended accounting, and kmem support. Tied to projects, zones, resource controls, and process membership.

## Research Notes
The header separates public task ID operations from kernel accounting/resource-control internals.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/task.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq.h

## Purpose
Defines the public kernel task queue interface for asynchronous work dispatch.

## Main Interfaces
- Types:
  - opaque `taskq_t`
  - `taskqid_t`
  - `task_func_t`
- Creation flags:
  - `TASKQ_PREPOPULATE`
  - `TASKQ_CPR_SAFE`
  - `TASKQ_DYNAMIC`
  - `TASKQ_THREADS_CPU_PCT`
  - `TASKQ_DC_BATCH`
  - `TASKQ_THREADS_LWP`
- Dispatch flags:
  - `TQ_SLEEP`
  - `TQ_NOSLEEP`
  - `TQ_NOQUEUE`
  - `TQ_NOALLOC`
  - `TQ_FRONT`
- `TASKQID_INVALID`.
- Kernel APIs:
  - initialization and MP initialization
  - create variants including instance, proc, and SDC-backed taskqs
  - `taskq_dispatch()`
  - wait/wait-by-id, destroy, empty, suspend/resume, membership check
  - `nulltask()`
- Global `system_taskq`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/thread.h`. Implementation details live in `taskq_impl.h`.

## Research Notes
`TQ_SLEEP` and `TQ_NOSLEEP` intentionally match kmem allocation semantics. Public flags occupy bits 0-15; implementation flags are reserved elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq_impl.h

## Purpose
Defines private taskq implementation structures, statistics, bucket state, internal flags, and preallocated dispatch support.

## Main Interfaces
- `taskq_ent_t`: queued task entry with list links, function, argument, bucket/flags union, executing thread, and completion CV.
- `TQENT_FLAG_PREALLOC`.
- `tqstat_t`: unlocked per-bucket statistics for hits, misses, dispatch-created tasks, overflow, backlog, thread creates/deaths, and max threads.
- `taskq_bucket_t`: per-CPU bucket with lock, enclosing taskq, backlog/freelist heads, allocation/backlog/free counts, CV, flags, total time, and stats.
- Bucket flags:
  - `TQBUCKET_CLOSE`
  - `TQBUCKET_SUSPEND`
  - `TQBUCKET_REDIRECT`
- Implementation taskq flags:
  - `TASKQ_CHANGING`
  - `TASKQ_SUSPENDED`
  - `TASKQ_NOINSTANCE`
  - `TASKQ_THREAD_CREATED`
  - `TASKQ_DUTY_CYCLE`
- `struct taskq`: full taskq state including locks/CVs, priority, flags, thread counts/limits, freelist, bucket array, instance, thread pointer/list, CPU percentage linkage, process/cpupart/SDC duty cycle, kstats, timing, counters, and dynamic-thread count.
- `taskq_dispatch_ent()`: special dispatch using caller-provided preallocated entries.
- `TASKQ_THREADS_PCT()`.

## Dependencies And Relationships
Includes taskq, integer, vmem, list, kstat, and rwlock headers. Used only by taskq implementation and tightly coupled to kernel threads, per-CPU buckets, kstats, and optional SDC behavior.

## Research Notes
The header documents that statistics are not lock-protected. Bucket distribution and preallocated entries are central to avoiding allocation in constrained dispatch paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/telioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/telioctl.h

## Purpose
Defines ioctls and mode bits for the telnet protocol STREAMS module.

## Main Interfaces
- Ioctl base `TELIOC`.
- Ioctls:
  - `TEL_IOC_ENABLE`: resume processing and forward normal data.
  - `TEL_IOC_MODE`: set data-processing mode.
  - `TEL_IOC_GETBLK`: request next network input message while disabled.
- Mode bits:
  - `TEL_BINARY_IN`
  - `TEL_BINARY_OUT`

## Dependencies And Relationships
Related to telnet module control and `logindmux.h` queue exchange behavior referenced in comments.

## Research Notes
The comments define operational semantics, including insertion of attached data at the head of the read queue for `TEL_IOC_ENABLE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/telioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem.h

## Purpose
Defines the kernel-facing terminal emulator public API for virtual terminal state creation, activation, mode changes, output, size queries, framebuffer mode, and STREAMS queue attachment.

## Main Interfaces
- Opaque types:
  - `tem_modechg_cb_arg_t`
  - `tem_modechg_cb_t`
  - `tem_vt_state_t`
- Kernel APIs:
  - `tem_initialized()`
  - `tem_init()`, `tem_destroy()`
  - `tem_info_init()`
  - `tem_write()`
  - `tem_safe_polled_write()`
  - `tem_get_size()`
  - `tem_register_modechg_cb()`
  - `tem_activate()`, `tem_switch()`
  - `tem_get_fbmode()`, `tem_set_fbmode()`
  - `tem_clean()`
  - `tem_init_q()`

## Dependencies And Relationships
Kernel-only includes STREAMS, visual I/O, credentials, and beep support. Private state and rendering callbacks are in `tem_impl.h`.

## Research Notes
The public header intentionally hides terminal parser and framebuffer/text rendering state behind `tem_vt_state_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem_impl.h

## Purpose
Defines private terminal emulator parser, color, screen-buffer, virtual-terminal, rendering-callback, and shared soft-state structures.

## Main Interfaces
- Character/attribute packing:
  - `tem_char_t`
  - `TEM_CHAR()`, `TEM_ATTR()`, `TEM_CHAR_ATTR()`, `TEM_ATTR_ISSET()`
  - attribute flags for reverse, bold, blink, underline, screen reverse, bright colors, transparency, image, and RGB foreground/background
- ANSI/parser constants:
  - `TEM_MAXPARAMS`, `TEM_MAXFKEY`
  - scroll/shift direction constants
  - ANSI color constants
  - parser states `A_STATE_START`, `A_STATE_ESC`, `A_STATE_CSI`, `A_STATE_CSI_QMARK`, `A_STATE_CSI_EQUAL`
- Default terminal dimensions and colors.
- Color and geometry types:
  - `text_color_t`
  - `text_attr_t`
  - `tem_color_t`
  - `tem_pix_pos`, `tem_char_pos`, `tem_size`
  - `term_char_t`
- `struct tem_vt_state`: per-VT parser/output state, locks, framebuffer mode, attributes, ANSI params, tabs, cursor positions, output buffers, pixel scratch area, colors, screen/history buffers, UTF-8 partial state, active/initialized/cursor state, and list node.
- `tem_safe_callbacks_t`: rendering callback table for display, copy, cursor, bit-to-pixel, and clear-screen operations.
- `tem_state_t`: shared terminal emulator soft state, layered device handle, display/pixel dimensions, font, callback set, active terminal, mode-change callback, color map, lock, and VT list.
- Globals:
  - `tems`
  - `tem_safe_text_callbacks`
  - `tem_safe_pix_callbacks`
- Internal functions for layered display/copy/cursor/clear, safe terminal emulation, text/pixel display paths, cursor, clear, color setting, and screen reset/restore.

## Dependencies And Relationships
Includes font, RGB, DDI/LDI, visual I/O, list, public `tem.h`, and annotation headers when not building boot code. Used by console terminal emulation and framebuffer/text console rendering.

## Research Notes
The screen buffer uses a combined 32-bit character/attribute representation with separate foreground/background color arrays in `term_char_t`. Comments note that console history would require revisiting the buffering model.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termio.h

## Purpose
Provides the legacy System V `termio` interface layered on top of `termios.h`.

## Main Interfaces
- `struct termio`: 16-bit input/output/control/local flags, line discipline, and `_NCC` control characters.
- `IOCTYPE`, `TCDSET`, and optional `TTYTYPE`.
- `struct termcb`: legacy line-discipline terminal control block.
- Default speed `SSPEED`.
- Terminal type constants such as `TERM_NONE`, `TERM_TEC`, `TERM_V61`, `TERM_V10`, and others.
- Terminal flag constants:
  - `TM_NONE`
  - `TM_SNL`
  - `TM_ANL`
  - `TM_LCF`
  - `TM_CECHO`
  - `TM_CINVIS`
  - `TM_SET`

## Dependencies And Relationships
Includes `sys/termios.h`, which supplies most ioctl codes and modern flag definitions.

## Research Notes
This is a compatibility header for older APIs. New terminal code generally uses `termios`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termios.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termios.h

## Purpose
Defines the POSIX and extended illumos terminal control ABI: `struct termios`, terminal flag types, control character indexes/defaults, input/output/control/local mode bits, ioctl numbers, speed constants, PPS event structures, and window-size structure.

## Main Interfaces
- Types:
  - `tcflag_t`
  - `cc_t`
  - `speed_t`
  - `struct termios`
- Userland APIs:
  - speed get/set helpers
  - `tcgetattr()`, `tcsetattr()`
  - `tcsendbreak()`, `tcdrain()`, `tcflush()`, `tcflow()`
  - `tcgetsid()` where exposed
- Control character indexes and defaults:
  - `VINTR`, `VQUIT`, `VERASE`, `VKILL`, `VEOF`, `VEOL`, `VMIN`, `VTIME`, `VSTART`, `VSTOP`, `VSUSP`, and extended indexes/defaults.
- Mode bit families:
  - input flags such as break/parity/CR/NL/flow-control handling
  - output flags and delay masks
  - control flags for character size, parity, hangup, local mode, hardware flow control, baud extension bits
  - local flags for signal/canonical/echo/job-control behavior
- Ioctl constants:
  - System V `TCGETA`/`TCSETA*`
  - POSIX `TCGETS`/`TCSETS*`
  - BSD/job-control/modem/pty compatibility ioctls
  - PPS ioctls and `struct ppsclockev`
- Speed constants from `B0` through `B4000000`.
- `struct winsize`.

## Dependencies And Relationships
Includes feature-test, tty device/time extensions, and types headers depending on standards exposure macros. Used by libc, terminal drivers, STREAMS modules, ptys, and compatibility layers.

## Research Notes
Large parts of the header are gated by `__XOPEN_OR_POSIX`, `_POSIX_C_SOURCE`, `_XPG6`, and `__EXTENSIONS__` to preserve standards visibility rules while still exposing illumos/BSD/System V extensions when requested.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termios.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termiox.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termiox.h

## Purpose
Defines the optional extended terminal interface for hardware flow control and clocking modes.

## Main Interfaces
- `NFF`: reserved field count.
- Hardware flow control flags:
  - `RTSXOFF`
  - `CTSXON`
  - `DTRXOFF`
  - `CDXON`
  - `ISXOFF`
- Clock source masks and values:
  - transmit clock `XMTCLK` family
  - receive clock `RCVCLK` family
  - transmitter signal element `TSETCLK` family
  - receiver signal element `RSETCLK` family
- `struct termiox`: hardware flags, clock flags, reserved flags, and spare flags.
- Ioctls:
  - `TCGETX`
  - `TCSETX`
  - `TCSETXW`
  - `TCSETXF`

## Dependencies And Relationships
Used by terminal/serial drivers that implement optional extended hardware flow-control and clocking semantics.

## Research Notes
The comments state that this interface is optional and may not be implemented on all machines.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/termiox.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/thread.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/thread.h

## Purpose
Defines the kernel thread object, thread states, scheduler/process flags, context operation hooks, active file descriptor tracking, wait-channel data, thread state manipulation macros, dispatcher locking helpers, stackinfo logging, and thread name support.

## Main Interfaces
- Thread states:
  - `TS_FREE`, `TS_SLEEP`, `TS_RUN`, `TS_ONPROC`, `TS_ZOMB`, `TS_STOPPED`, `TS_WAIT`
- Supporting structures:
  - `ctxop_t`: context save/restore/fork/lwp-create/exit/free hooks.
  - `afd_t`: per-thread active file descriptor table.
  - `lwpchan_t`: wait-channel uniqueness.
  - `kthread_id_t`, `kt_did_t`
- `kthread_t`: central kernel thread structure containing dispatch links, stack/PC, CPU binding, flags, scheduler state/priorities, PCB, wait channel, scheduling class data, fault state, locks, CPU/PIL/migration state, LWP/process/signal/audit/credential state, dispatcher lock pointer, syscall/post-trap flags, microstate profiling, turnstile priority inheritance state, TSD, doors, scheduler activation state, copyops, active fd table, sleep/wait queues, project/zone, taskq marker, DTrace state, user access state, wait mutex, name, and SMT-safety flag.
- Flag families:
  - `T_*` thread flags
  - `TP_*` process/LWP flags
  - `TS_*` scheduler flags
  - CPU/pset binding flags and helpers
- State/test macros:
  - `aston()`, `astoff()`
  - `ISTOPPED()`, `ISWAKEABLE()`, `ISWAITING()`, CPR variants
  - `VSTOPPED()`, `SUSPENDED()`, `INHERITED()`
  - priority and process/LWP conversion macros
- Kernel globals/functions:
  - `curthread`, `curproc`, `curproj`, `curzone`
  - `t0`, `pidlock`
  - thread free prevent/allow
  - priority-change helpers
  - `thread_transition()`, `thread_stop()`, `thread_lock*()`, `thread_onproc()`
  - stack init, thread naming
- State transition macros:
  - `THREAD_CHANGE_PRI()`, `THREAD_WILLCHANGE_PRI()`
  - `THREAD_RUN()`, `THREAD_WAIT()`, `THREAD_SWAP()`, `THREAD_ZOMB()`, `THREAD_ONPROC()`, `THREAD_SLEEP()`, `THREAD_FREEINTR()`
- Stackinfo constants and `kmem_stkinfo_t`.

## Dependencies And Relationships
Includes types, locks, LWP, time, signal, and KCPC headers. It is foundational for scheduler, process, syscall, DTrace, taskq, wait queue, and synchronization code.

## Research Notes
The structure is highly compatibility-sensitive inside the kernel. Comments document which fields are protected by thread locks, process locks, no locks, or current-thread-only modification rules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticlts.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticlts.h

## Purpose
Defines compatibility error macros for the connectionless TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings:
  - `TCL_BADADDR`
  - `TCL_BADOPT`
  - `TCL_NOPEER`
  - `TCL_PEERBADSTATE`

## Dependencies And Relationships
Used by old TICLTS consumers and documentation compatibility. Error values map to standard `errno` constants.

## Research Notes
The file explicitly says these old error codes are exposed only for compatibility and should not be used in new programs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticlts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticots.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticots.h

## Purpose
Defines compatibility error macros for the connection-oriented TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings for bad address/options, connection/reference errors, listener queue full, outstanding indications, no peer, bad peer state, and missing connection indications.

## Dependencies And Relationships
Used by legacy TICOTS consumers and compatibility documentation. Error values map to standard `errno` constants.

## Research Notes
Like `ticlts.h`, this is explicitly compatibility-only and not intended for new code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticots.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticotsord.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticotsord.h

## Purpose
Defines compatibility error macros for the orderly-release connection-oriented TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings parallel TICOTS: address/options, connection/reference errors, full listener queue, outstanding indications, missing peer, bad peer state, and missing connection indications.

## Dependencies And Relationships
Used by old TICOTSORD consumers and compatibility documentation.

## Research Notes
The macros are retained only for old manual-page/API compatibility and should not be used in new programs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticotsord.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tihdr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tihdr.h

## Purpose
Defines TPI protocol primitive numbers, state values, primitive structures, kernel-only extended primitives, capability structures, option headers, and option alignment/traversal macros.

## Main Interfaces
- Primitive constants for connection, disconnection, data, expedited data, info, bind/unbind, unitdata, option management, orderly release, address, capability, and kernel extended primitives.
- State constants including TPI provider/user state machine values and `TS_NOSTATES`.
- Core TPI structures:
  - `T_conn_req`, `T_conn_res`, `T_discon_req`
  - `T_data_req`, `T_exdata_req`
  - `T_info_req`
  - `T_bind_req`, `T_unbind_req`
  - `T_unitdata_req`
  - `T_optmgmt_req`
  - `T_ordrel_req`
  - `T_addr_req`
  - corresponding indication/ack/error structures such as `T_conn_ind`, `T_conn_con`, `T_discon_ind`, `T_data_ind`, `T_exdata_ind`, `T_info_ack`, `T_bind_ack`, `T_error_ack`, `T_ok_ack`, `T_unitdata_ind`, `T_uderror_ind`, `T_optmgmt_ack`, `T_ordrel_ind`, and `T_addr_ack`
- Capability support:
  - `T_capability_req`
  - `T_capability_ack`
- Kernel extended structures:
  - `T_optdata_req`, `T_optdata_ind`, `T_extconn_ind`, and related extended primitive values.
- `struct T_opthdr`: TPI option header.
- Alignment and option iteration macros:
  - `__TPI_ALIGN()`, `__TPI_SIZE_ISALIGNED()`
  - primitive/option alignment helpers
  - `_TPI_TOPT_DATA()`, `_TPI_TOPT_DATALEN()`
  - `_TPI_TOPT_FIRSTHDR()`, `_TPI_TOPT_NEXTHDR()`, `_TPI_TOPT_VALID()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/tpicommon.h`. Used by STREAMS TPI providers/consumers and kernel transport interfaces such as `t_kuser.h`.

## Research Notes
The header is version-sensitive through `_SUN_TPI_VERSION`, exposing old/new primitive names and capability support depending on the selected TPI version.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tihdr.h -->
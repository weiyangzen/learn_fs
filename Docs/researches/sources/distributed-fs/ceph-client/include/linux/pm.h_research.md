# sources/distributed-fs/ceph-client/include/linux/pm.h

## Purpose
the central Linux device power-management interface. It defines system sleep callbacks, runtime PM
state, wakeup-source accounting, PM messages, event constants, and helper APIs shared by drivers and
core code.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PM_H`, `power_group_name`, `SYSTEM_SLEEP_PM_OPS`,
`LATE_SYSTEM_SLEEP_PM_OPS`, `NOIRQ_SYSTEM_SLEEP_PM_OPS`, `RUNTIME_PM_OPS`,
`SET_SYSTEM_SLEEP_PM_OPS`, `SET_LATE_SYSTEM_SLEEP_PM_OPS`, `SET_NOIRQ_SYSTEM_SLEEP_PM_OPS`,
`SET_RUNTIME_PM_OPS`, `_DEFINE_DEV_PM_OPS`, `_EXPORT_PM_OPS`, `_DISCARD_PM_OPS`,
`_EXPORT_DEV_PM_OPS`, and 83 more. Types: `struct pm_message`, `struct pm_subsys_data`, `struct
dev_pm_info`, `struct dev_pm_domain`, `enum rpm_status`, `enum rpm_request`, `enum dpm_order`,
`typedef struct pm_message {`. Declared or inline functions: `void`, `pm_vt_switch_required`,
`pm_vt_switch_unregister`, `cxl_mem_active`, `int`, `__EXPORT_SYMBOL`, `dev_pm_get_subsys_data`,
`dev_pm_put_subsys_data`, `device_pm_lock`, `dpm_resume_start`, `dpm_resume_end`,
`dpm_resume_noirq`, `dpm_resume_early`, `dpm_resume`, `dpm_complete`, `device_pm_unlock`,
`dpm_suspend_end`, `dpm_suspend_start`, and 27 more. Important struct details: struct pm_message
fields include `int event`, `} pm_message_t`, `int (*prepare)(struct device *dev)`, `void
(*complete)(struct device *dev)`, `int (*suspend)(struct device *dev)`, `int (*resume)(struct device
*dev)`, `int (*freeze)(struct device *dev)`, `int (*thaw)(struct device *dev)`; struct
pm_subsys_data fields include `spinlock_t lock`, `unsigned int refcount`, `unsigned int
clock_op_might_sleep`, `struct mutex clock_mutex`, `struct list_head clock_list`, `struct
pm_domain_data *domain_data`; struct dev_pm_info fields include `pm_message_t power_state`, `bool
can_wakeup:1`, `bool async_suspend:1`, `bool in_dpm_list:1`, `bool is_prepared:1`, `bool
is_suspended:1`, `bool is_noirq_suspended:1`, `bool is_late_suspended:1`; struct dev_pm_domain
fields include `struct dev_pm_ops ops`, `int (*start)(struct device *dev)`, `void (*detach)(struct
device *dev, bool power_off)`, `int (*activate)(struct device *dev)`, `void (*sync)(struct device
*dev)`, `void (*dismiss)(struct device *dev)`, `int (*set_performance_state)(struct device *dev,
unsigned int state)`. Important enum details: enum rpm_status values include `RPM_INVALID`,
`RPM_ACTIVE`, `RPM_RESUMING`, `RPM_SUSPENDED`, `RPM_SUSPENDING`, `RPM_BLOCKED`; enum rpm_request
values include `RPM_REQ_NONE`, `RPM_REQ_IDLE`, `RPM_REQ_SUSPEND`, `RPM_REQ_AUTOSUSPEND`,
`RPM_REQ_RESUME`; enum dpm_order values include `DPM_ORDER_NONE`, `DPM_ORDER_DEV_AFTER_PARENT`,
`DPM_ORDER_PARENT_BEFORE_DEV`, `DPM_ORDER_DEV_LAST`.

## Control flow
Device drivers or bus types populate `struct dev_pm_ops` callbacks; the PM core runs prepare,
suspend or hibernation callbacks, noirq phases, resume or restore callbacks, and completion
callbacks in ordered device-tree or dependency order. Runtime PM helpers update `struct
dev_pm_info`, wakeup accounting, timers, locks, and work items as drivers request autosuspend,
forbid/allow runtime PM, or mark devices active/suspended.

## State and persistence
State is embedded in `struct dev_pm_info`, wakeup-source objects, completion objects, timers, wait
queues, spinlocks, mutexes, and work items owned by each device. It is runtime kernel state, not
filesystem persistence; suspend and hibernation preserve or restore hardware and memory according to
the selected callbacks.

## Dependencies and integration points
It includes `linux/completion.h`, `linux/export.h`, `linux/hrtimer_types.h`, `linux/mutex.h`,
`linux/spinlock.h`, `linux/types.h`, `linux/util_macros.h`, `linux/wait.h`,
`linux/workqueue_types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/sound/hda/core/regmap.c`, `sources/distributed-fs/ceph-
client/sound/ac97/bus.c`, `sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos_scb_lib.c`,
`sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.c`, `sources/distributed-fs/ceph-
client/sound/pci/cs46xx/cs46xx_lib.c`, `sources/distributed-fs/ceph-client/sound/hda/common/bind.c`,
`sources/distributed-fs/ceph-client/sound/hda/common/codec.c`, `sources/distributed-fs/ceph-
client/arch/arm64/kernel/hibernate.c`. It integrates with the driver core, bus types, PM domains,
wakeup-source code, runtime PM, suspend/hibernate sequencing, and architecture/platform suspend
backends.

## Risks and test signals
Risks concentrate around callback ordering, direct-complete decisions, async suspend races, wakeup-
source reference leaks, runtime PM usage-count imbalance, noirq operations that sleep, and
hibernation restore paths diverging from suspend/resume. Test signals include suspend-to-idle,
suspend-to-RAM, hibernation, runtime autosuspend stress, wakeup-source accounting, lockdep,
`pm_test` modes, and driver unbind during PM transitions.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pm.h` completely for this pass (913 lines, 37678 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pm.h_research.md`.

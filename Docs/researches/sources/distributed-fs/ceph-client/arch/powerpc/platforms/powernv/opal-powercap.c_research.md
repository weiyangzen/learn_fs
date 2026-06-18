## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-powercap.c

### Purpose
`opal-powercap.c` creates `/sys/firmware/opal/powercap` attribute groups for OPAL power capping handles, allowing current caps to be read and, where supported, written.

### Important APIs, Types, And Functions
The main types are `struct powercap_attr` and the `pcaps` array. Important functions are `powercap_show()`, `powercap_store()`, `powercap_add_attr()`, and `opal_powercap_init()`.

### Control Flow
Initialization finds `ibm,opal-powercap`, creates a `powercap` kobject, then for each child creates attributes based on `powercap-min`, `powercap-max`, and `powercap-current` properties. Reads allocate an async OPAL token, take `powercap_mutex`, call `opal_get_powercap()`, wait if needed, and print the big-endian result. Writes parse a numeric cap, use the same token/mutex pattern with `opal_set_powercap()`, and return `count` on success.

### State, Persistence, And Dependencies
Linux state is the kobject, per-child attribute groups, handles, and a mutex serializing firmware calls. Persistent values live in OPAL/platform power policy. Dependencies include OPAL async completion, `opal_error_code()`, sysfs/kobject APIs, and OF child properties.

### Integration Points
`opal_init()` calls this after `opal_kobj` exists. User space interacts through sysfs, and firmware validates/updates cap values.

### Risks
Some failure paths free only groups already counted by `i`, so partial setup must be scrutinized. Attribute `name` strings point at DT property/static strings for cap files and allocated group names for nodes. All firmware calls are serialized globally, which is simple but can block unrelated cap reads.

### Test Signals
Test child nodes with every property combination, async and immediate OPAL responses, interrupted token or mutex acquisition, invalid numeric writes, min/max read-only permissions, current write permissions, and cleanup after mid-loop allocation/sysfs failures.

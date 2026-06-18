## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sysparam.c

### Purpose
`opal-sysparam.c` exposes OPAL system parameters as sysfs files under `/sys/firmware/opal/sysparams`, using firmware-described IDs, sizes, names, and permissions.

### Important APIs, Types, And Functions
The central type is `struct param_attr`. Important functions are `opal_get_sys_param()`, `opal_set_sys_param()`, `sys_param_show()`, `sys_param_store()`, and `opal_sys_param_init()`.

### Control Flow
Initialization validates `/ibm,opal/sysparams`, creates a kobject, allocates a shared 64-byte transaction buffer, reads parameter names, IDs, lengths, and permissions, and creates sysfs files whose modes reflect read/write flags. Reads lock `opal_sysparam_mutex`, call async `opal_get_param()`, copy the fixed-size result into `buf`, and return the parameter size. Writes clamp input to 64 bytes, copy it into the shared buffer, call async `opal_set_param()` with the DT-declared parameter size, and return the user count on success.

### State, Persistence, And Dependencies
State is the kobject, shared buffer, allocated attribute array, and mutex. Parameter values persist in OPAL/platform firmware. Dependencies include OPAL async tokens, `opal_error_code()`, DT property arrays, sysfs, and kobject lifetime.

### Integration Points
`opal_init()` calls this once `opal_kobj` is available. User space reads and writes sysfs files to query or update platform parameters.

### Risks
`sys_param_store()` clamps the copied user count but still sends `attr->param_size` bytes to firmware, so if `count` is shorter than the parameter size, trailing bytes are whatever remained in the shared buffer. Attribute objects are allocated as one array and not retained in a global pointer for removal. DT array count consistency is assumed after each read.

### Test Signals
Test missing/incompatible node, mismatched property counts, parameters larger than 64 bytes, read-only/write-only/read-write modes, short writes, async wait failures, interrupted token allocation, concurrent sysfs access, and cleanup after sysfs creation failures.

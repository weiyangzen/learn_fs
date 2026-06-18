# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-ci.c

## Purpose
`ddbridge-ci.c` implements Common Interface (CI/CAM) support for Digital Devices bridge cards. It supports internal CI register-backed interfaces, external XO2 I2C-backed interfaces, and Sony CXD2099-based CI bridges, all exposed through the DVB EN50221 CA API.

## Important APIs, Types, And Functions
Public entry points are `ddb_ci_attach()` and `ddb_ci_detach()`. Internal EN50221 callbacks include `read_attribute_mem()`, `write_attribute_mem()`, `read_cam_control()`, `write_cam_control()`, `slot_reset()`, `slot_shutdown()`, `slot_ts_enable()`, and `poll_slot_status()` for internal CI, with `_xo2` equivalents for XO2. Helpers include `wait_ci_ready()`, `ci_attach()`, `write_creg()`, `ci_xo2_attach()`, and `ci_cxd2099_attach()`. `en_templ` and `en_xo2_templ` are callback templates; `cxd_cfgtmpl` configures CXD2099.

## Control Flow
Internal CI access writes bridge command registers such as `CI_DO_READ_ATTRIBUTES()`, waits for `CI_READY`, and reads `CI_BUFFER()` or `CI_READDATA()`. Slot reset powers the CAM, asserts reset, enables the interface, delays, and releases reset. XO2 access uses `i2c_read_reg*()`/`i2c_write_reg*()` at address `0x12` or `0x13` based on port type; control register writes update cached `port->creg`. CXD2099 attach clones the config, installs `port->en`, and probes the `cxd2099` module at I2C address `0x40`. `ddb_ci_attach()` dispatches by `port->type`, ensures `port->en`, and calls `dvb_ca_en50221_init()`. Detach unregisters any DVB device, releases EN50221, releases the optional I2C client, frees template-allocated data when owned, and clears `port->en`.

## State, Persistence, And Dependencies
Runtime state is in allocated `struct ddb_ci`, `port->en`, `port->en_freedata`, `port->creg`, and `port->dvb[0].i2c_client[0]`. There is no disk persistence. Dependencies include ddbridge register/IO/I2C helpers, `dvb_ca_en50221`, `dvb_module_probe()`/`release()`, port type constants, and CXD2099 configuration.

## Integration Points
The file is linked into `ddbridge.o` and called from core port setup/teardown when a CI-capable port is detected. It bridges low-level hardware operations to the standard DVB CA interface consumed by userspace CAM tools and demux pipelines.

## Risks
Ready waits return `-1` on timeout but some callers ignore the result after writes, so hardware stalls may surface as later EN50221 errors. Address bounds use `address > CI_BUFFER_SIZE`, leaving `address == CI_BUFFER_SIZE` to wrap via the mask; this boundary should be reviewed against hardware expectations. Ownership differs between CXD2099 (`port->en_freedata = 0`) and locally allocated templates, so detach order is lifetime-sensitive. XO2 I2C failures in reset/shutdown helpers are mostly ignored.

## Test Signals
Test internal, XO2, XO2_B, and Sony external CI ports with CAM insertion/removal, attribute memory reads, CAM control reads/writes, TS enable/bypass, reset/shutdown, timeout behavior, module unload/reload, and EN50221 userspace operations such as CAM menu access.

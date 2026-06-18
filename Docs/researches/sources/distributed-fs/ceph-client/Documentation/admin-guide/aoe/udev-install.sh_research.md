<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh

### Purpose
Installs AoE-specific udev rules from udev.txt into the system udev rules directory.

### Important APIs, Types, And Functions
The script finds udev.conf from $conf, /etc/udev/udev.conf, or find /etc; extracts udev_rules, defaults to /etc/udev/rules.d, validates the directory, and copies dirname($0)/udev.txt to 60-aoe.rules using sh -xc.

### Control Flow
Persistent effect is writing a udev rules file under the selected rules directory.

### State, Persistence, And Dependencies
State is shell variables for config and rules path; no runtime daemon state. Depends on /bin/sh, basename, find, sed, dirname, cp, and root/write permission.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include command injection/word splitting through sh -xc and unquoted variables, multiple udev.conf paths from find, and no atomic copy.

### Test Signals
Test signals include env-provided conf, missing conf, missing rules dir, and copy from a fixture script directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh -->

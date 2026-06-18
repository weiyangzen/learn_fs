<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh

### Purpose
Installs modprobe aliases so the ATA over Ethernet kernel module can autoload for major 152 block and char devices.

### Important APIs, Types, And Functions
The script sets f=/etc/modprobe.d/aoe.conf, checks it is readable and writable, greps for major-152, and appends alias lines when absent.

### Control Flow
Control flow is simple shell validation and append. It exits 1 when the config file cannot be accessed.

### State, Persistence, And Dependencies
Persistent effect is editing /etc/modprobe.d/aoe.conf. Depends on /bin/sh, grep, shell redirection, and root/write permission to /etc/modprobe.d.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include unquoted $f, requiring the file to already exist, duplicate detection matching any major-152 text, and no atomic update.

### Test Signals
Test signals include existing alias no-op, missing file failure, unwritable file failure, and successful append under a temp root or container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh -->

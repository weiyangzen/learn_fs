<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh -->
## sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh

### Purpose
Autogenerates a /tmp/mkdev3270 shell script to create s390 3270 tty/tub device nodes and update /etc/inittab.

### Important APIs, Types, And Functions
Key variables define proc driver path, root/dev directories, output script paths, inittab paths, and mingetty line template. The script probes /proc/tty/driver/tty3270, modprobes tub3270 if needed, queries config, and writes shell commands.

### Control Flow
It initializes output scripts, optionally removes/recreates /dev/3270, filters existing inittab tty lines, reads driver device rows, writes mknod/chmod commands and mingetty entries, appends inittab replacement commands, and exits.

### State, Persistence, And Dependencies
Persistent effects happen only when the generated /tmp/mkdev3270 is later run; this script itself writes /tmp/mkdev3270 and temporary /tmp/mkdev3270.a. Depends on /bin/sh, modprobe, /proc tty3270 interface, mknod, chmod, grep, mv, /etc/inittab style init systems, and s390 device major/minor semantics.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include legacy init assumptions, unquoted variables, destructive generated commands, /tmp path predictability, and root requirements.

### Test Signals
Test signals include running against a mocked proc file, generated script diffing, missing driver exit, and no /dev/dasd conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh -->

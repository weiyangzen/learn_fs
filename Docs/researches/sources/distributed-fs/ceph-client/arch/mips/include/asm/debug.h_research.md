<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h

**Purpose:** Declares the top-level MIPS debugfs directory.

**Important APIs/types/functions:** Extern `struct dentry *mips_debugfs_dir`.

**Control flow:** No code; MIPS debugfs users create files below this dentry.

**State, dependencies, integration:** Integrates architecture debug facilities with Linux debugfs.

**Risks and test signals:** Users must handle debugfs disabled or directory not initialized. Test debugfs entry creation/removal and CONFIG_DEBUG_FS off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h -->

## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec1.c

### Purpose
`pwc-dec1.c` contains the initialization stub for codec version 1 decompression used by older Nala webcams.

### Important APIs, Types, And Functions
The only function is `pwc_dec1_init(struct pwc_device *pdev, const unsigned char *cmd)`, which stores `pdev->release` in `pdev->dec1.version`.

### Control Flow
The function is called from Nala video-mode setup when a compressed mode is selected for YUV420 output. It does not parse the mode command or build decode tables.

### State, Persistence, And Dependencies
State is limited to `struct pwc_dec1_private.version` in the union inside `struct pwc_device`. The file depends on `pwc.h` for the device layout.

### Integration Points
`pwc-ctrl.c` invokes this initializer, while `pwc-uncompress.c` detects codec1 compressed YUV and currently returns `-ENXIO` instead of decompressing. Raw PWC1 output can still expose compressed data to userspace.

### Risks
The initializer can make codec1 compressed modes appear prepared, but kernel-side decompression is intentionally missing. Applications requesting YUV420 on compressed codec1 hardware will fail during buffer finish.

### Test Signals
Use an older codec1 camera and request raw PWC1 versus YUV420 compressed modes. Raw output should carry metadata; YUV decompression should fail clearly with the existing unsupported path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h

Purpose: Provides IIO-specific sysfs attribute wrappers and declaration macros.

Important APIs/types/functions: `struct iio_dev_attr` extends `device_attribute` with an address/private value; `struct iio_const_attr` exposes constant strings. Macros declare generic IIO attrs, device attrs, named attrs, constant attrs, and common sampling frequency, integration time, and temperature attributes.

Control flow: IIO core and drivers declare attributes statically; sysfs invokes show/store callbacks or constant readers.

State/persistence: Attribute metadata is static. Per-device values are read or written through callbacks; constants persist as literal strings.

Dependencies/integration: Integrates with Linux device attributes, IIO buffers/channels, and common IIO ABI filenames.

Risks: Attribute mode/callback mismatches can create write-only/read-only ABI bugs; incorrect address values can direct callbacks to wrong registers.

Test signals: Sysfs file existence, permissions, const-attr output, read/write callback routing, and ABI filename stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sysfs.h -->

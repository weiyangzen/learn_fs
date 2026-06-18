# sources/distributed-fs/coda/coda-src/norton/norton-print.cc

Purpose: legacy print helpers for version vectors and volume summaries. It overlaps with newer printing code in `norton-volume.cc`.

APIs: `PrintVV` formats raw version-vector fields, and `print_volume` prints ID, name, parent, group ID, partition, version vector, and small/large vnode list counts/pointers.

Dependencies and risks: includes older preprocessor syntax in `extern "C"` guards and uses fixed format assumptions for pointer-sized values. Because `norton-volume.cc` also defines `print_volume`, this file must not be linked into the same target unless duplicate definitions are intentionally avoided. Test signal is build/link success for any target that still references it.

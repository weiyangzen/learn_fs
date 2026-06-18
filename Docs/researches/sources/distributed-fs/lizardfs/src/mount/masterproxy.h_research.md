## sources/distributed-fs/lizardfs/src/mount/masterproxy.h

Purpose: declares the three-function API for the local master proxy: initialize, terminate, and rewrite masterinfo location.

Important APIs: `masterproxy_getlocation(uint8_t *masterinfo)` mutates the serialized masterinfo buffer in place; `masterproxy_init()` returns positive success or negative failure; `masterproxy_term()` stops the proxy thread.

Integration: used by special inode reads for `MASTERINFO` and initialized/terminated by the mount/client lifecycle when proxy support is enabled.

Risks and tests: the in-place 14-byte buffer contract is implicit and must match `fs_getmasterlocation`. Tests should validate that proxy location is not advertised before successful init or for older master versions.

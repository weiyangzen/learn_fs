<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h

Purpose: defines Rockchip crypto register offsets/bits, shared device/variant/context structures, algorithm template declarations, and MMIO access macros.

Important APIs and types: register definitions cover interrupt status/enable, control, configuration, DMA source/length registers, AES, TDES, and hash engines. `struct rockchip_ip` owns the global device list and debugfs state. `struct rk_variant` describes required clocks and maximum rates. `struct rk_crypto_info` stores one hardware instance, runtime resources, crypto engine, completion, and status. Hash and cipher transform/request contexts hold fallback transforms, keys, IV backup, mode, and request state. `struct rk_crypto_tmp` wraps skcipher or ahash engine algorithms with statistics.

Control flow and integration: core driver registers extern `rk_crypto_tmp` templates declared here. Algorithm files use register constants and `CRYPTO_READ`/`CRYPTO_WRITE` to program hardware. `get_rk_crypto()` is the common device selector for algorithm code.

State and persistence: transform contexts persist fallback objects and key material; request contexts persist selected device/mode and fallback requests. Device and global list state persist across requests and probes.

Dependencies: crypto engine, AES/DES/hash APIs, DMA mapping, interrupts, runtime PM, scatterlists, and Rockchip hardware register ABI.

Risks and test signals: register constants include a misspelled `RK_CYYPTO_*` name but values are used as constants. Key/IV sizes and register byte-swap flags are central to correctness. Test compile coverage for all extern templates, runtime PM request paths, and register programming for AES/DES/hash modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h -->

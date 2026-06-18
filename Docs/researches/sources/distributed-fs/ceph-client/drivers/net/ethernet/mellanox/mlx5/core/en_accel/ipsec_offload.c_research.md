# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_offload.c

Purpose: owns IPsec hardware capability discovery, encryption key/general-object creation, object modification, ASO query/update plumbing, and hardware event handling for ESN and lifetime events.

Important APIs/types/functions: `mlx5_ipsec_device_caps`, `mlx5_ipsec_create_sa_ctx`, `mlx5_ipsec_free_sa_ctx`, `mlx5_accel_esp_modify_xfrm`, `mlx5e_ipsec_aso_init/cleanup`, and `mlx5e_ipsec_aso_query`. Internals include packet ASO setup, create/destroy/modify IPsec object commands, ASO soft/hard lifetime updates, ESN event update, notifier callback, and event work handler.

Control flow and state: capability probing checks global IPsec support, DEK, general object types, flow-table crypto capabilities, AES-GCM support, packet/crypto/tunnel/ESP-in-UDP/priority/RoCE/ESN features. SA context creation first creates a crypto key, then a general IPsec object; packet offload embeds ASO context, PD, return register, replay/lifetime settings, and increment/replay modes. ASO init maps a DMA buffer, creates a global ASO SQ, registers object-change notifier, and serializes ASO WQ access with a spinlock. Events query ASO state under XFRM lock, handle lifetime expiration rounds, and modify object attrs on ESN changes.

Dependencies and integration: uses mlx5 command interface, crypto key pool, ASO library, notifier, device caps, flow steering object IDs, XFRM locks, and attrs from `ipsec.c`.

Risks and test signals: capability bits gate user-visible features; key/object creation must unwind cleanly; ASO polling timeout or event ordering can miss ESN/lifetime transitions; object modify requires firmware support bits. Test devices with partial caps, 128/256-bit keys, packet lifetime soft/hard limits, ESN inbound/outbound rollover, ASO query failure, notifier cleanup, and SA create failure after key creation.

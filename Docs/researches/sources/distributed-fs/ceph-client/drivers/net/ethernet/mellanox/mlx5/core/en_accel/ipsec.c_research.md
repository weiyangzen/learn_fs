# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec.c

Purpose: integrates mlx5e with Linux XFRM device offload for IPsec ESP. It validates XFRM states/policies, translates them into driver attributes, owns SA/policy lifecycle, handles ESN/lifetime/neighbour work, and publishes netdev offload features.

Important APIs/types/functions: exported `mlx5e_ipsec_init`, `mlx5e_ipsec_cleanup`, `mlx5e_ipsec_build_netdev`, and `mlx5e_ipsec_build_accel_xfrm_attrs`. XFRM callbacks include state add/delete/free/advance ESN/update stats and policy add/delete/free. Helpers manage ESN state, packet lifetime math, MAC resolution for tunnel packet offload, validation, delayed software limit checks, and neighbour events.

Control flow and state: init allocates `struct mlx5e_ipsec`, initializes SADB xarray/workqueue/completion, optional ASO and netevent notifier, flow steering, and attaches it to `priv`. State add allocates `mlx5e_ipsec_sa_entry`, validates AES-GCM ESP constraints, blocks eswitch conflicts, checks tunnel permission, initializes ESN and attrs, creates optional work/dwork, creates HW SA context, installs flow rules, inserts into SADB, and stores `xso.offload_handle`. Delete erases from SADB; free cancels work, deletes flow rules, frees HW context, unblocks eswitch, and frees memory. Policy add builds masked selector attrs and installs flow rules similarly.

Dependencies and integration: relies on XFRM core, Linux crypto AEAD/geniv, neighbour/FIB lookup, eswitch block APIs, mlx5 IPsec hardware context creation, IPsec flow steering, and ASO event support.

Risks and test signals: validation must reject unsupported algorithms, replay windows, limits, encap, and policies; resource unwinding has many partial states; tunnel MAC resolution can temporarily mark SAs drop until neighbour update. Test crypto and packet offload, IPv4/IPv6 transport/tunnel, ESN rollover, lifetime soft/hard expiration, neighbour updates, policy priorities, acquire states, stats update, and cleanup with pending work.

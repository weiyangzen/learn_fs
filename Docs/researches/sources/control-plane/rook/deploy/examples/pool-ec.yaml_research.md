# sources/control-plane/rook/deploy/examples/pool-ec.yaml

Purpose: defines a simple erasure-coded block pool example.

Important APIs/types/functions: `CephBlockPool/ec-pool`, failure domain `host`, EC profile `dataChunks: 2`, `codingChunks: 1`, and compression disabled.

Control flow: Rook creates the EC profile and pool in Ceph.

State and persistence: data written to the pool is stored with EC layout across OSDs.

Dependencies/integration: requires enough OSDs and failure domains for 2+1 EC placement.

Risks: EC pools have workload and feature constraints compared to replicated pools and may need special storage class settings for RBD.

Test signals: pool ready, Ceph health clean, and pool detail shows the expected EC profile.

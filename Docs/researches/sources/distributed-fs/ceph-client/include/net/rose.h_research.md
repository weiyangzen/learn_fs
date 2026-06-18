# sources/distributed-fs/ceph-client/include/net/rose.h

Purpose: defines the ROSE network address length constant.

Important APIs and types: `ROSE_ADDR_LEN` is set to 5. No functions or structs are declared.

Control flow: ROSE protocol code includes this header when sizing or validating ROSE addresses.

State and persistence: no state.

Dependencies and integration points: integrates with AX.25/ROSE networking code that handles fixed-size ROSE addresses.

Risks and test signals: risk is limited to address-size mismatches. Test compile users and ROSE address parse/format paths.

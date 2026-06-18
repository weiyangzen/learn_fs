# sources/distributed-fs/ceph-client/include/dt-bindings/arm/ux500_pm_domains.h

Purpose: defines Ux500 power-domain IDs for device-tree consumers.

Important APIs/types/functions: `DOMAIN_VAPE` is domain 0 and `NR_DOMAINS` derives the domain count.

Control flow: DTS power-domain references use the ID; PM domain provider code indexes the corresponding domain.

State and persistence: the numeric ID is DT ABI. No runtime state is stored.

Dependencies and integration: standalone binding used by Ux500 DTS and generic PM domain provider/consumers.

Risks and test signals: adding domains requires preserving existing IDs and updating `NR_DOMAINS`. Test DT references and genpd provider registration.

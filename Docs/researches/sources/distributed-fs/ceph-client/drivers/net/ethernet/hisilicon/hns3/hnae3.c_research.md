# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.c

## Purpose

`hnae3.c` implements the HNAE3 framework registry that binds acceleration-engine devices, acceleration-engine algorithms, and clients such as the kernel NIC and RoCE clients. It serializes registration/unregistration, initializes matching AE devices, instantiates/uninstantiates clients, and coordinates unload ordering.

## Important APIs, Types, And Functions

The file owns three global lists: `hnae3_ae_algo_list`, `hnae3_client_list`, and `hnae3_ae_dev_list`. It exports `hnae3_unregister_ae_algo_prepare`, `hnae3_acquire_unload_lock`, `hnae3_release_unload_lock`, `hnae3_set_client_init_flag`, `hnae3_register_client`, `hnae3_unregister_client`, `hnae3_register_ae_algo`, `hnae3_unregister_ae_algo`, `hnae3_register_ae_dev`, and `hnae3_unregister_ae_dev`.

Internal helpers include `hnae3_client_match`, `hnae3_get_client_init_flag`, `hnae3_init_client_instance`, and `hnae3_uninit_client_instance`. The framework relies on `struct hnae3_client`, `struct hnae3_ae_dev`, `struct hnae3_ae_algo`, PCI ID matching, AE ops such as `init_ae_dev`, `uninit_ae_dev`, `init_client_instance`, and `uninit_client_instance`, and flag bits such as `HNAE3_DEV_INITED_B`, `HNAE3_KNIC_CLIENT_INITED_B`, and `HNAE3_ROCE_CLIENT_INITED_B`.

## Control Flow

Client registration validates uniqueness by client type, adds the client, then attempts to initialize it on all already-initialized matching AE devices. Client unregistration verifies existence, uninitializes the client on each matching initialized AE device, and removes it from the list.

AE algorithm registration adds the algorithm, scans existing AE devices, matches PCI IDs, assigns ops, initializes the AE device, marks it initialized, then initializes every registered client on it. AE algorithm unregistration scans initialized matching devices, uninitializes all clients, uninitializes the AE device, clears init state and ops, then removes the algorithm.

AE device registration adds the device, scans existing algorithms for a matching PCI ID, initializes the AE device through the first matching algorithm, marks it initialized, then initializes all registered clients. If algorithm init fails, the device is removed from the list. AE device unregistration uninitializes clients and AE state for any matching initialized algorithm, clears ops, and removes the device.

`hnae3_unregister_ae_algo_prepare` is a pre-unregister hook that disables SR-IOV on initialized matching PCI devices under the PCI device lock when PCI IOV is enabled.

## State And Persistence

State is global and in-memory: the three lists, `hnae3_common_lock` protecting registry updates, `hnae3_unload_lock` serializing driver unloads, per-device ops pointer, and per-device init/client bits. There is no persistent storage across module unload.

## Dependencies And Integration Points

The framework depends on Linux list/mutex/PCI APIs and `hnae3.h`. It is the rendezvous point for HNS3 PF/VF AE algorithms and upper clients. It exports symbols so separate modules can register in any order while still matching already-registered peers.

## Risks And Test Signals

Risks include duplicate AE algorithm registration not being checked by name, partial client initialization failures being logged but not rolled back globally, ordering issues when unregistering while clients or devices are probing, SR-IOV disable side effects during algorithm removal, and reliance on clients setting/clearing init flags consistently. Test signals include module load/unload in every order, PF/VF probe after client-first and device-first registration, RoCE and KNIC coexistence, SR-IOV enabled removal, no stale list nodes after failure paths, and lockdep-clean unload serialization.

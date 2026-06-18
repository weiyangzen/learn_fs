# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure.go

This file initializes Azure Key Vault as a KMS backend and adapts Kubernetes client-certificate secrets into the file-based format expected by the Azure secrets library.

`IsAzure()` checks whether the provider is `secrets.TypeAzure`. `InitAzure()` calls `azureKVCert()` to prepare connection details, defers certificate cleanup, converts `map[string]string` to `map[string]interface{}`, and constructs the Azure secrets client with `azure.New()`. `azureKVCert()` requires `AZURE_CERT_SECRET_NAME`, fetches that Kubernetes Secret from the provided namespace, writes the `CLIENT_CERT` key to a temporary `cert.pem` file with mode `0400`, and stores the generated path in `azure.AzureClientCertPath`. It returns a cleanup function built from the shared temp-file cleanup helper and eagerly removes files on setup errors.

State includes a temporary certificate file and the mutable connection-details map. Dependencies include Kubernetes CoreV1 Secrets, libopenstorage Azure secrets, and clusterd context. Risks include expecting a specific `CLIENT_CERT` key, mutating caller config, cleanup timing while initializing the client, and typoed mandatory details variable name. `azure_test.go` validates missing secret name, missing secret, successful temp file creation, and cleanup.

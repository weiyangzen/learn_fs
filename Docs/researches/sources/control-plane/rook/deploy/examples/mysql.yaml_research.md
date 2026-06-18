# sources/control-plane/rook/deploy/examples/mysql.yaml

Purpose: provides the MySQL half of the classic WordPress example, using Rook-backed dynamic storage through a PVC.

Important APIs/types/functions: `Service/wordpress-mysql`, `PersistentVolumeClaim/mysql-pv-claim`, and `Deployment/wordpress-mysql` using image `mysql:5.6`.

Control flow: the headless MySQL service selects pods labeled `app=wordpress,tier=mysql`; the deployment mounts the PVC at MySQL data storage and configures the database via environment variables.

State and persistence: database files are persisted in `mysql-pv-claim`, whose `storageClassName` is expected to point to a Rook Ceph block storage class.

Dependencies/integration: pairs with `wordpress.yaml` and requires a `rook-ceph-block` or equivalent storage class.

Risks: MySQL 5.6 is old for production use, example credentials are static, and PVC binding fails if the storage class is absent.

Test signals: PVC binds, MySQL pod becomes ready, and WordPress can connect to the service name.
